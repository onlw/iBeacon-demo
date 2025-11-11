"""
Real-time iBeacon Distance Monitor
Distance monitoring tool with real-time chart visualization
"""
import asyncio
import math
from bleak import BleakScanner
from ibeacon_parser import IBeaconParser
from typing import Optional, List
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import numpy as np

# Matplotlib configuration
import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False


class RealtimeDistanceMonitor:
    """Real-time Distance Monitor (with visualization)"""

    def __init__(self, environment_factor: float = 3.0, history_size: int = 50):
        """
        Initialize monitor

        Args:
            environment_factor: Environment attenuation factor
            history_size: Number of historical data points to keep
        """
        self.environment_factor = environment_factor
        self.history_size = history_size

        # Data storage
        self.timestamps = deque(maxlen=history_size)
        self.distances = deque(maxlen=history_size)
        self.rssi_values = deque(maxlen=history_size)

        # Target beacon
        self.target_beacon = None
        self.beacon_info = {}

        # Visualization
        self.fig = None
        self.axes = None

    def calculate_distance(self, rssi: int, tx_power: int) -> float:
        """Calculate distance"""
        if rssi == 0:
            return -1.0

        ratio = (tx_power - rssi) / (10.0 * self.environment_factor)
        distance = math.pow(10, ratio)

        return distance

    def setup_plot(self):
        """Setup visualization charts"""
        plt.style.use('seaborn-v0_8-darkgrid')
        self.fig, self.axes = plt.subplots(2, 1, figsize=(12, 8))

        # Distance chart
        self.axes[0].set_title('Real-time Distance Monitoring', fontsize=14, fontweight='bold')
        self.axes[0].set_xlabel('Time (seconds)')
        self.axes[0].set_ylabel('Distance (meters)')
        self.axes[0].grid(True, alpha=0.3)

        # RSSI chart
        self.axes[1].set_title('RSSI Signal Strength', fontsize=14, fontweight='bold')
        self.axes[1].set_xlabel('Time (seconds)')
        self.axes[1].set_ylabel('RSSI (dBm)')
        self.axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

    def update_plot(self):
        """Update charts"""
        if not self.timestamps:
            return

        # Clear charts
        for ax in self.axes:
            ax.clear()

        # Time axis (relative time)
        times = [(t - self.timestamps[0]).total_seconds() for t in self.timestamps]

        # Distance chart
        self.axes[0].plot(times, list(self.distances), 'b-', linewidth=2, label='Distance')
        self.axes[0].fill_between(times, 0, list(self.distances), alpha=0.3)
        self.axes[0].set_title('Real-time Distance Monitoring', fontsize=14, fontweight='bold')
        self.axes[0].set_xlabel('Time (seconds)')
        self.axes[0].set_ylabel('Distance (meters)')
        self.axes[0].grid(True, alpha=0.3)
        self.axes[0].legend()

        # Add distance range markers
        self.axes[0].axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='Immediate')
        self.axes[0].axhline(y=2.0, color='orange', linestyle='--', alpha=0.5, label='Near')
        self.axes[0].axhline(y=5.0, color='yellow', linestyle='--', alpha=0.5, label='Medium')

        # Display current distance
        if self.distances:
            current_dist = self.distances[-1]
            self.axes[0].text(0.02, 0.98, f'Current: {current_dist:.2f}m',
                            transform=self.axes[0].transAxes,
                            verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                            fontsize=12, fontweight='bold')

        # RSSI chart
        self.axes[1].plot(times, list(self.rssi_values), 'g-', linewidth=2, label='RSSI')
        self.axes[1].fill_between(times, list(self.rssi_values), alpha=0.3)
        self.axes[1].set_title('RSSI Signal Strength', fontsize=14, fontweight='bold')
        self.axes[1].set_xlabel('Time (seconds)')
        self.axes[1].set_ylabel('RSSI (dBm)')
        self.axes[1].grid(True, alpha=0.3)
        self.axes[1].legend()

        # Display current RSSI
        if self.rssi_values:
            current_rssi = self.rssi_values[-1]
            self.axes[1].text(0.02, 0.98, f'Current: {current_rssi} dBm',
                            transform=self.axes[1].transAxes,
                            verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
                            fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.pause(0.01)

    async def monitor(self,
                     target_uuid: Optional[str] = None,
                     target_major: Optional[int] = None,
                     target_minor: Optional[int] = None,
                     scan_interval: float = 1.0,
                     show_plot: bool = True):
        """
        Start monitoring

        Args:
            target_uuid: Target UUID
            target_major: Target Major
            target_minor: Target Minor
            scan_interval: Scan interval (seconds)
            show_plot: Whether to show charts
        """
        print("=" * 70)
        print("Real-time iBeacon Distance Monitor")
        print("=" * 70)
        print(f"Scan interval: {scan_interval} seconds")
        print(f"Environment factor: {self.environment_factor}")
        print("Press Ctrl+C to stop monitoring")
        print("=" * 70)
        print()

        if show_plot:
            self.setup_plot()
            plt.ion()  # Interactive mode
            plt.show()

        try:
            while True:
                current_beacon = None

                def detection_callback(device, advertisement_data):
                    nonlocal current_beacon

                    beacon_data = IBeaconParser.parse(
                        advertisement_data.manufacturer_data,
                        advertisement_data.rssi
                    )

                    if beacon_data:
                        # Check target matching
                        if target_uuid and beacon_data.uuid != target_uuid:
                            return
                        if target_major is not None and beacon_data.major != target_major:
                            return
                        if target_minor is not None and beacon_data.minor != target_minor:
                            return

                        # Lock target
                        if not self.target_beacon:
                            self.target_beacon = (beacon_data.uuid, beacon_data.major, beacon_data.minor)
                            self.beacon_info = {
                                'uuid': beacon_data.uuid,
                                'major': beacon_data.major,
                                'minor': beacon_data.minor,
                                'tx_power': beacon_data.tx_power
                            }
                            print(f"\nTarget iBeacon locked:")
                            print(f"  UUID: {beacon_data.uuid}")
                            print(f"  Major: {beacon_data.major}")
                            print(f"  Minor: {beacon_data.minor}")
                            print(f"  TxPower: {beacon_data.tx_power} dBm\n")

                        if self.target_beacon == (beacon_data.uuid, beacon_data.major, beacon_data.minor):
                            current_beacon = beacon_data

                # Scan
                scanner = BleakScanner(detection_callback=detection_callback)
                await scanner.start()
                await asyncio.sleep(scan_interval)
                await scanner.stop()

                # Process data
                if current_beacon:
                    # Calculate distance
                    distance = self.calculate_distance(
                        current_beacon.rssi,
                        current_beacon.tx_power
                    )

                    # Add to history
                    self.timestamps.append(datetime.now())
                    self.distances.append(distance)
                    self.rssi_values.append(current_beacon.rssi)

                    # Print info
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Distance: {distance:.2f}m | RSSI: {current_beacon.rssi} dBm")

                    # Update charts
                    if show_plot:
                        self.update_plot()

                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Warning: Signal lost")

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")
            if show_plot:
                plt.ioff()
                print("\nChart window remains open, close it to exit...")
                plt.show()


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Real-time iBeacon Distance Monitor')
    parser.add_argument('--uuid', type=str, help='Target UUID')
    parser.add_argument('--major', type=int, help='Target Major')
    parser.add_argument('--minor', type=int, help='Target Minor')
    parser.add_argument('--env-factor', type=float, default=2,
                       help='Environment attenuation factor (default: 2.0)')
    parser.add_argument('--interval', type=float, default=3.0,
                       help='Scan interval in seconds (default: 3.0)')
    parser.add_argument('--no-plot', action='store_true',
                       help='Disable chart display')

    args = parser.parse_args()

    print(args)
    monitor = RealtimeDistanceMonitor(environment_factor=args.env_factor)

    await monitor.monitor(
        target_uuid=args.uuid,
        target_major=args.major,
        target_minor=args.minor,
        scan_interval=args.interval,
        show_plot=not args.no_plot
    )


if __name__ == '__main__':
    asyncio.run(main())
