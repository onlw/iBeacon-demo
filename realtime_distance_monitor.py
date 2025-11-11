"""
实时 iBeacon 距离监控程序
带有实时图表可视化的距离监控工具
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


class RealtimeDistanceMonitor:
    """实时距离监控器（带可视化）"""

    def __init__(self, environment_factor: float = 3.0, history_size: int = 50):
        """
        初始化监控器

        Args:
            environment_factor: 环境衰减因子
            history_size: 历史数据保存数量
        """
        self.environment_factor = environment_factor
        self.history_size = history_size

        # 数据存储
        self.timestamps = deque(maxlen=history_size)
        self.distances = deque(maxlen=history_size)
        self.rssi_values = deque(maxlen=history_size)

        # 目标 beacon
        self.target_beacon = None
        self.beacon_info = {}

        # 可视化
        self.fig = None
        self.axes = None

    def calculate_distance(self, rssi: int, tx_power: int) -> float:
        """计算距离"""
        if rssi == 0:
            return -1.0

        ratio = (tx_power - rssi) / (10.0 * self.environment_factor)
        distance = math.pow(10, ratio)

        # 分段校准
        if distance < 0.5:
            distance = distance * 0.9
        elif distance < 1.0:
            distance = distance * 0.95
        elif distance > 10.0:
            distance = distance * 1.1

        return distance

    def setup_plot(self):
        """设置可视化图表"""
        plt.style.use('seaborn-v0_8-darkgrid')
        self.fig, self.axes = plt.subplots(2, 1, figsize=(12, 8))

        # 距离图表
        self.axes[0].set_title('实时距离监控', fontsize=14, fontweight='bold')
        self.axes[0].set_xlabel('时间 (秒)')
        self.axes[0].set_ylabel('距离 (米)')
        self.axes[0].grid(True, alpha=0.3)

        # RSSI 图表
        self.axes[1].set_title('RSSI 信号强度', fontsize=14, fontweight='bold')
        self.axes[1].set_xlabel('时间 (秒)')
        self.axes[1].set_ylabel('RSSI (dBm)')
        self.axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

    def update_plot(self):
        """更新图表"""
        if not self.timestamps:
            return

        # 清空图表
        for ax in self.axes:
            ax.clear()

        # 时间轴 (相对时间)
        times = [(t - self.timestamps[0]).total_seconds() for t in self.timestamps]

        # 距离图表
        self.axes[0].plot(times, list(self.distances), 'b-', linewidth=2, label='距离')
        self.axes[0].fill_between(times, 0, list(self.distances), alpha=0.3)
        self.axes[0].set_title('实时距离监控', fontsize=14, fontweight='bold')
        self.axes[0].set_xlabel('时间 (秒)')
        self.axes[0].set_ylabel('距离 (米)')
        self.axes[0].grid(True, alpha=0.3)
        self.axes[0].legend()

        # 添加距离区间标记
        self.axes[0].axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='紧邻')
        self.axes[0].axhline(y=2.0, color='orange', linestyle='--', alpha=0.5, label='近距离')
        self.axes[0].axhline(y=5.0, color='yellow', linestyle='--', alpha=0.5, label='中距离')

        # 显示当前距离
        if self.distances:
            current_dist = self.distances[-1]
            self.axes[0].text(0.02, 0.98, f'当前距离: {current_dist:.2f}m',
                            transform=self.axes[0].transAxes,
                            verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                            fontsize=12, fontweight='bold')

        # RSSI 图表
        self.axes[1].plot(times, list(self.rssi_values), 'g-', linewidth=2, label='RSSI')
        self.axes[1].fill_between(times, list(self.rssi_values), alpha=0.3)
        self.axes[1].set_title('RSSI 信号强度', fontsize=14, fontweight='bold')
        self.axes[1].set_xlabel('时间 (秒)')
        self.axes[1].set_ylabel('RSSI (dBm)')
        self.axes[1].grid(True, alpha=0.3)
        self.axes[1].legend()

        # 显示当前 RSSI
        if self.rssi_values:
            current_rssi = self.rssi_values[-1]
            self.axes[1].text(0.02, 0.98, f'当前 RSSI: {current_rssi} dBm',
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
        开始监控

        Args:
            target_uuid: 目标 UUID
            target_major: 目标 Major
            target_minor: 目标 Minor
            scan_interval: 扫描间隔 (秒)
            show_plot: 是否显示图表
        """
        print("=" * 70)
        print("实时 iBeacon 距离监控")
        print("=" * 70)
        print(f"扫描间隔: {scan_interval} 秒")
        print(f"环境衰减因子: {self.environment_factor}")
        print("按 Ctrl+C 停止监控")
        print("=" * 70)
        print()

        if show_plot:
            self.setup_plot()
            plt.ion()  # 交互模式
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
                        # 检查目标匹配
                        if target_uuid and beacon_data.uuid != target_uuid:
                            return
                        if target_major is not None and beacon_data.major != target_major:
                            return
                        if target_minor is not None and beacon_data.minor != target_minor:
                            return

                        # 锁定目标
                        if not self.target_beacon:
                            self.target_beacon = (beacon_data.uuid, beacon_data.major, beacon_data.minor)
                            self.beacon_info = {
                                'uuid': beacon_data.uuid,
                                'major': beacon_data.major,
                                'minor': beacon_data.minor,
                                'tx_power': beacon_data.tx_power
                            }
                            print(f"\n✓ 锁定目标 iBeacon:")
                            print(f"  UUID: {beacon_data.uuid}")
                            print(f"  Major: {beacon_data.major}")
                            print(f"  Minor: {beacon_data.minor}")
                            print(f"  TxPower: {beacon_data.tx_power} dBm\n")

                        if self.target_beacon == (beacon_data.uuid, beacon_data.major, beacon_data.minor):
                            current_beacon = beacon_data

                # 扫描
                scanner = BleakScanner(detection_callback=detection_callback)
                await scanner.start()
                await asyncio.sleep(scan_interval)
                await scanner.stop()

                # 处理数据
                if current_beacon:
                    # 计算距离
                    distance = self.calculate_distance(
                        current_beacon.rssi,
                        current_beacon.tx_power
                    )

                    # 添加到历史
                    self.timestamps.append(datetime.now())
                    self.distances.append(distance)
                    self.rssi_values.append(current_beacon.rssi)

                    # 打印信息
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"距离: {distance:.2f}m | RSSI: {current_beacon.rssi} dBm")

                    # 更新图表
                    if show_plot:
                        self.update_plot()

                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ 信号丢失")

        except KeyboardInterrupt:
            print("\n\n监控已停止")
            if show_plot:
                plt.ioff()
                print("\n图表窗口保持打开，关闭窗口以退出...")
                plt.show()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='实时 iBeacon 距离监控')
    parser.add_argument('--uuid', type=str, help='目标 UUID')
    parser.add_argument('--major', type=int, help='目标 Major')
    parser.add_argument('--minor', type=int, help='目标 Minor')
    parser.add_argument('--env-factor', type=float, default=3.0,
                       help='环境衰减因子 (默认: 3.0)')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='扫描间隔/秒 (默认: 1.0)')
    parser.add_argument('--no-plot', action='store_true',
                       help='禁用图表显示')

    args = parser.parse_args()

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
