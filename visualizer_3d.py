"""
3D Visualization Module
Real-time display of position and beacon distribution using matplotlib
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Dict, Optional
import threading

# Matplotlib configuration
import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False


class Visualizer3D:
    """Real-time 3D Visualizer"""

    def __init__(self, beacon_positions: Dict[str, np.ndarray], room_size: tuple = (10, 10, 5)):
        """
        Initialize visualizer

        Args:
            beacon_positions: {beacon_name: np.array([x, y, z])} beacon position dictionary
            room_size: Room dimensions (width, depth, height)
        """
        self.beacon_positions = beacon_positions
        self.room_size = room_size
        self.current_position = None
        self.position_history = []
        self.max_history = 50  # Keep maximum 50 historical positions

        # Create figure
        plt.ion()  # Enable interactive mode
        self.fig = plt.figure(figsize=(12, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Initialize plot elements
        self.beacon_scatter = None
        self.position_scatter = None
        self.trajectory_line = None
        self.distance_lines = []

        self._setup_plot()

    def _setup_plot(self):
        """Setup plot style and range"""
        self.ax.set_xlabel('X (m)', fontsize=10)
        self.ax.set_ylabel('Y (m)', fontsize=10)
        self.ax.set_zlabel('Z (m)', fontsize=10)
        self.ax.set_title('iBeacon Indoor 3D Positioning System', fontsize=14, fontweight='bold')

        # Set coordinate range
        self.ax.set_xlim(0, self.room_size[0])
        self.ax.set_ylim(0, self.room_size[1])
        self.ax.set_zlim(0, self.room_size[2])

        # Draw room boundary (optional)
        self._draw_room_boundary()

        # Draw beacon positions (fixed)
        self._draw_beacons()

        self.ax.legend(loc='upper right', fontsize=8)
        self.fig.tight_layout()

    def _draw_room_boundary(self):
        """Draw room boundary box"""
        w, d, h = self.room_size

        # Bottom surface
        self.ax.plot([0, w], [0, 0], [0, 0], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [0, d], [0, 0], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, 0], [d, d], [0, 0], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([0, 0], [d, 0], [0, 0], 'k--', alpha=0.3, linewidth=0.5)

        # Top surface
        self.ax.plot([0, w], [0, 0], [h, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [0, d], [h, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, 0], [d, d], [h, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([0, 0], [d, 0], [h, h], 'k--', alpha=0.3, linewidth=0.5)

        # Vertical edges
        self.ax.plot([0, 0], [0, 0], [0, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [0, 0], [0, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [d, d], [0, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([0, 0], [d, d], [0, h], 'k--', alpha=0.3, linewidth=0.5)

    def _draw_beacons(self):
        """Draw beacon positions"""
        if not self.beacon_positions:
            return

        positions = np.array(list(self.beacon_positions.values()))
        names = list(self.beacon_positions.keys())

        # Draw beacon points
        self.beacon_scatter = self.ax.scatter(
            positions[:, 0], positions[:, 1], positions[:, 2],
            c='red', marker='^', s=200, alpha=0.8,
            edgecolors='darkred', linewidths=2,
            label='Beacon'
        )

        # Add beacon labels
        for name, pos in self.beacon_positions.items():
            self.ax.text(pos[0], pos[1], pos[2] + 0.2, name,
                        fontsize=8, ha='center', color='darkred', weight='bold')

    def update(self, position: Optional[np.ndarray], beacon_distances: Optional[Dict[str, float]] = None):
        """
        Update visualization

        Args:
            position: Current position [x, y, z], if None then don't update position
            beacon_distances: {beacon_name: distance} distance to each beacon
        """
        if position is None:
            return

        self.current_position = position

        # Update position history
        self.position_history.append(position.copy())
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)

        # Clear previous current position and trajectory
        if self.position_scatter is not None:
            self.position_scatter.remove()
        if self.trajectory_line is not None:
            self.trajectory_line.remove()

        # Clear previous distance lines
        for line in self.distance_lines:
            line.remove()
        self.distance_lines.clear()

        # Draw current position
        self.position_scatter = self.ax.scatter(
            position[0], position[1], position[2],
            c='blue', marker='o', s=300, alpha=1.0,
            edgecolors='darkblue', linewidths=2,
            label='Current Position'
        )

        # Draw movement trajectory
        if len(self.position_history) > 1:
            history_array = np.array(self.position_history)
            self.trajectory_line, = self.ax.plot(
                history_array[:, 0], history_array[:, 1], history_array[:, 2],
                'b-', alpha=0.5, linewidth=1.5, label='Trajectory'
            )

        # Draw distance lines to beacons (optional)
        if beacon_distances:
            for beacon_name, distance in beacon_distances.items():
                if beacon_name in self.beacon_positions:
                    beacon_pos = self.beacon_positions[beacon_name]
                    line, = self.ax.plot(
                        [position[0], beacon_pos[0]],
                        [position[1], beacon_pos[1]],
                        [position[2], beacon_pos[2]],
                        'g--', alpha=0.3, linewidth=1
                    )
                    self.distance_lines.append(line)

                    # Display distance at midpoint
                    mid_point = (position + beacon_pos) / 2
                    text = self.ax.text(
                        mid_point[0], mid_point[1], mid_point[2],
                        f'{distance:.1f}m', fontsize=7, color='green'
                    )
                    self.distance_lines.append(text)

        # Update legend
        handles, labels = self.ax.get_legend_handles_labels()
        # Remove duplicates (repeated drawing creates duplicate legends)
        by_label = dict(zip(labels, handles))
        self.ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8)

        # Refresh display
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

    def close(self):
        """Close visualization window"""
        plt.ioff()
        plt.close(self.fig)

    def show(self):
        """Show visualization window (blocking)"""
        plt.ioff()
        plt.show()
