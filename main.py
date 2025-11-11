"""
iBeacon 室内 3D 定位系统主程序
"""
import asyncio
import json
import numpy as np
from typing import Dict
from ibeacon_scanner import IBeaconScanner
from positioning_3d import Position3D, KalmanFilter3D
from visualizer_3d import Visualizer3D
import signal
import sys


class IBeaconPositioningSystem:
    """iBeacon 定位系统主类"""

    def __init__(self, config_file: str = 'beacon_config.json'):
        """
        初始化定位系统

        Args:
            config_file: 配置文件路径
        """
        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 初始化组件
        self.scanner = IBeaconScanner(
            environment_factor=self.config['environment_factor']
        )
        self.position_calculator = Position3D()
        self.kalman_filter = KalmanFilter3D(
            process_variance=1e-3,
            measurement_variance=1.5
        )

        # 构建 beacon 位置映射
        self.beacon_positions = {}
        self.beacon_map = {}  # {(uuid, major, minor): {'name': ..., 'position': ...}}

        for beacon in self.config['beacons']:
            key = (beacon['uuid'], beacon['major'], beacon['minor'])
            position = np.array(beacon['position'])
            name = beacon['name']

            self.beacon_map[key] = {
                'name': name,
                'position': position
            }
            self.beacon_positions[name] = position

        # 初始化可视化器
        room_size = self.config.get('room_size', [20, 15, 5])
        self.visualizer = Visualizer3D(
            beacon_positions=self.beacon_positions,
            room_size=tuple(room_size)
        )

        # 运行状态
        self.running = True
        self.current_position = None

    def _process_scan_results(self, scanned_beacons: Dict):
        """
        处理扫描结果并更新位置

        Args:
            scanned_beacons: 扫描到的 beacon 数据
        """
        # 匹配扫描到的 beacon 与配置的 beacon
        matched_beacons = []
        beacon_distances = {}

        for key, data in scanned_beacons.items():
            if key in self.beacon_map:
                beacon_info = self.beacon_map[key]
                position = beacon_info['position']
                distance = data['distance']
                name = beacon_info['name']

                matched_beacons.append((position, distance))
                beacon_distances[name] = distance

                print(f"  {name}: {distance:.2f}m (RSSI: {data['beacon_data'].rssi}dBm)")

        # 检查是否有足够的 beacon
        min_beacons = self.config.get('min_beacons_required', 3)
        if len(matched_beacons) < min_beacons:
            print(f"⚠ 检测到的 beacon 数量不足 ({len(matched_beacons)}/{min_beacons})，无法定位")
            return

        # 过滤异常值
        filtered_beacons = self.position_calculator.filter_outliers(
            matched_beacons,
            max_distance=50.0
        )

        if len(filtered_beacons) < min_beacons:
            print(f"⚠ 过滤后的 beacon 数量不足 ({len(filtered_beacons)}/{min_beacons})，无法定位")
            return

        # 计算位置（使用最小二乘法）
        raw_position = self.position_calculator.least_squares_3d(filtered_beacons)

        if raw_position is not None:
            # 使用卡尔曼滤波平滑位置
            smoothed_position = self.kalman_filter.update(raw_position)
            self.current_position = smoothed_position

            print(f"📍 估算位置: X={smoothed_position[0]:.2f}m, "
                  f"Y={smoothed_position[1]:.2f}m, Z={smoothed_position[2]:.2f}m")

            # 更新可视化
            self.visualizer.update(smoothed_position, beacon_distances)

    async def run(self):
        """运行定位系统"""
        print("=" * 60)
        print("iBeacon 室内 3D 定位系统")
        print("=" * 60)
        print(f"配置的 Beacon 数量: {len(self.beacon_map)}")
        print(f"环境衰减因子: {self.config['environment_factor']}")
        print(f"扫描间隔: {self.config['scan_interval']}秒")
        print("按 Ctrl+C 停止程序")
        print("=" * 60)
        print()

        scan_interval = self.config.get('scan_interval', 1.0)

        try:
            while self.running:
                print(f"\n{'='*60}")
                print("🔍 正在扫描 iBeacon...")

                # 扫描 beacon
                beacons = await self.scanner.scan(duration=scan_interval)

                if beacons:
                    print(f"✓ 检测到 {len(beacons)} 个 iBeacon:")
                    self._process_scan_results(beacons)
                else:
                    print("⚠ 未检测到任何 iBeacon")

                # 短暂暂停
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n正在停止...")
        finally:
            self.stop()

    def stop(self):
        """停止系统"""
        self.running = False
        print("系统已停止")

    def show_visualization(self):
        """显示可视化（阻塞，用于最后）"""
        self.visualizer.show()


def signal_handler(sig, frame):
    """信号处理器（Ctrl+C）"""
    print("\n\n接收到中断信号，正在退出...")
    sys.exit(0)


async def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    # 创建并运行系统
    system = IBeaconPositioningSystem('beacon_config.json')

    try:
        await system.run()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 保持窗口打开
        input("\n按 Enter 键关闭可视化窗口...")
        system.visualizer.close()


if __name__ == '__main__':
    asyncio.run(main())
