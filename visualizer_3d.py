"""
3D 可视化模块
使用 matplotlib 实时显示位置和 beacon 分布
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Dict, Optional
import threading


class Visualizer3D:
    """3D 实时可视化器"""

    def __init__(self, beacon_positions: Dict[str, np.ndarray], room_size: tuple = (10, 10, 5)):
        """
        初始化可视化器

        Args:
            beacon_positions: {beacon_name: np.array([x, y, z])} beacon 位置字典
            room_size: 房间尺寸 (width, depth, height)
        """
        self.beacon_positions = beacon_positions
        self.room_size = room_size
        self.current_position = None
        self.position_history = []
        self.max_history = 50  # 最多保留 50 个历史位置

        # 创建图形
        plt.ion()  # 开启交互模式
        self.fig = plt.figure(figsize=(12, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # 初始化绘图元素
        self.beacon_scatter = None
        self.position_scatter = None
        self.trajectory_line = None
        self.distance_lines = []

        self._setup_plot()

    def _setup_plot(self):
        """设置绘图样式和范围"""
        self.ax.set_xlabel('X (m)', fontsize=10)
        self.ax.set_ylabel('Y (m)', fontsize=10)
        self.ax.set_zlabel('Z (m)', fontsize=10)
        self.ax.set_title('iBeacon Indoor 3D Positioning System', fontsize=14, fontweight='bold')

        # 设置坐标范围
        self.ax.set_xlim(0, self.room_size[0])
        self.ax.set_ylim(0, self.room_size[1])
        self.ax.set_zlim(0, self.room_size[2])

        # 绘制房间边界（可选）
        self._draw_room_boundary()

        # 绘制 beacon 位置（固定）
        self._draw_beacons()

        self.ax.legend(loc='upper right', fontsize=8)
        self.fig.tight_layout()

    def _draw_room_boundary(self):
        """绘制房间边界框"""
        w, d, h = self.room_size

        # 底面
        self.ax.plot([0, w], [0, 0], [0, 0], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [0, d], [0, 0], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, 0], [d, d], [0, 0], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([0, 0], [d, 0], [0, 0], 'k--', alpha=0.3, linewidth=0.5)

        # 顶面
        self.ax.plot([0, w], [0, 0], [h, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [0, d], [h, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, 0], [d, d], [h, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([0, 0], [d, 0], [h, h], 'k--', alpha=0.3, linewidth=0.5)

        # 竖直边
        self.ax.plot([0, 0], [0, 0], [0, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [0, 0], [0, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([w, w], [d, d], [0, h], 'k--', alpha=0.3, linewidth=0.5)
        self.ax.plot([0, 0], [d, d], [0, h], 'k--', alpha=0.3, linewidth=0.5)

    def _draw_beacons(self):
        """绘制 beacon 位置"""
        if not self.beacon_positions:
            return

        positions = np.array(list(self.beacon_positions.values()))
        names = list(self.beacon_positions.keys())

        # 绘制 beacon 点
        self.beacon_scatter = self.ax.scatter(
            positions[:, 0], positions[:, 1], positions[:, 2],
            c='red', marker='^', s=200, alpha=0.8,
            edgecolors='darkred', linewidths=2,
            label='Beacon'
        )

        # 添加 beacon 标签
        for name, pos in self.beacon_positions.items():
            self.ax.text(pos[0], pos[1], pos[2] + 0.2, name,
                        fontsize=8, ha='center', color='darkred', weight='bold')

    def update(self, position: Optional[np.ndarray], beacon_distances: Optional[Dict[str, float]] = None):
        """
        更新可视化

        Args:
            position: 当前位置 [x, y, z]，如果为 None 则不更新位置
            beacon_distances: {beacon_name: distance} 到每个 beacon 的距离
        """
        if position is None:
            return

        self.current_position = position

        # 更新位置历史
        self.position_history.append(position.copy())
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)

        # 清除之前的当前位置和轨迹
        if self.position_scatter is not None:
            self.position_scatter.remove()
        if self.trajectory_line is not None:
            self.trajectory_line.remove()

        # 清除之前的距离线
        for line in self.distance_lines:
            line.remove()
        self.distance_lines.clear()

        # 绘制当前位置
        self.position_scatter = self.ax.scatter(
            position[0], position[1], position[2],
            c='blue', marker='o', s=300, alpha=1.0,
            edgecolors='darkblue', linewidths=2,
            label='Current Position'
        )

        # 绘制移动轨迹
        if len(self.position_history) > 1:
            history_array = np.array(self.position_history)
            self.trajectory_line, = self.ax.plot(
                history_array[:, 0], history_array[:, 1], history_array[:, 2],
                'b-', alpha=0.5, linewidth=1.5, label='Trajectory'
            )

        # 绘制到 beacon 的距离线（可选）
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

                    # 在线中点显示距离
                    mid_point = (position + beacon_pos) / 2
                    text = self.ax.text(
                        mid_point[0], mid_point[1], mid_point[2],
                        f'{distance:.1f}m', fontsize=7, color='green'
                    )
                    self.distance_lines.append(text)

        # 更新图例
        handles, labels = self.ax.get_legend_handles_labels()
        # 去重（因为重复绘制会产生重复图例）
        by_label = dict(zip(labels, handles))
        self.ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8)

        # 刷新显示
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

    def close(self):
        """关闭可视化窗口"""
        plt.ioff()
        plt.close(self.fig)

    def show(self):
        """显示可视化窗口（阻塞）"""
        plt.ioff()
        plt.show()
