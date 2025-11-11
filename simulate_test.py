"""
模拟 iBeacon 扫描（用于测试）
在没有真实 Beacon 的情况下测试定位系统
"""
import asyncio
import numpy as np
from positioning_3d import Position3D, KalmanFilter3D
from visualizer_3d import Visualizer3D
import time


class SimulatedBeacon:
    """模拟 Beacon"""

    def __init__(self, name, position, uuid, major, minor, tx_power=-59):
        self.name = name
        self.position = np.array(position)
        self.uuid = uuid
        self.major = major
        self.minor = minor
        self.tx_power = tx_power

    def get_rssi(self, user_position, environment_factor=2.5):
        """
        根据用户位置计算 RSSI

        Args:
            user_position: 用户位置 [x, y, z]
            environment_factor: 环境衰减因子

        Returns:
            模拟的 RSSI 值
        """
        # 计算真实距离
        distance = np.linalg.norm(user_position - self.position)

        # 添加一些随机噪声（模拟真实环境）
        distance += np.random.normal(0, 0.2)  # 20cm 标准差

        # 根据距离计算 RSSI
        # RSSI = TxPower - 10*n*log10(distance)
        if distance < 0.1:
            distance = 0.1  # 避免 log(0)

        rssi = self.tx_power - 10 * environment_factor * np.log10(distance)
        rssi += np.random.normal(0, 2)  # 添加 RSSI 噪声

        return int(rssi)


class SimulationSystem:
    """模拟定位系统"""

    def __init__(self):
        # 创建模拟 Beacon（5m x 5m 房间，四个角）
        self.beacons = [
            SimulatedBeacon("Beacon-1", [0, 0, 2.5], "FDA50693-A4E2-4FB1-AFCF-C6EB07647825", 1, 1),
            SimulatedBeacon("Beacon-2", [5, 0, 2.5], "FDA50693-A4E2-4FB1-AFCF-C6EB07647825", 1, 2),
            SimulatedBeacon("Beacon-3", [5, 5, 2.5], "FDA50693-A4E2-4FB1-AFCF-C6EB07647825", 1, 3),
            SimulatedBeacon("Beacon-4", [0, 5, 2.5], "FDA50693-A4E2-4FB1-AFCF-C6EB07647825", 1, 4),
        ]

        # 准备 Beacon 位置映射
        beacon_positions = {b.name: b.position for b in self.beacons}

        # 初始化组件
        self.position_calculator = Position3D()
        self.kalman_filter = KalmanFilter3D()
        self.visualizer = Visualizer3D(beacon_positions, room_size=(6, 6, 3.5))

        # 模拟路径：圆形轨迹
        self.t = 0

    def get_simulated_position(self):
        """
        生成模拟的用户位置（圆形轨迹）

        Returns:
            模拟位置 [x, y, z]
        """
        # 圆形轨迹：中心 (2.5, 2.5, 1.5)，半径 1.5m
        center = np.array([2.5, 2.5, 1.5])
        radius = 1.5

        x = center[0] + radius * np.cos(self.t)
        y = center[1] + radius * np.sin(self.t)
        z = center[2]  # 高度固定

        self.t += 0.1  # 增加时间
        return np.array([x, y, z])

    def simulate_scan(self, user_position, environment_factor=2.5):
        """
        模拟 Beacon 扫描

        Args:
            user_position: 用户真实位置
            environment_factor: 环境衰减因子

        Returns:
            [(beacon_position, distance), ...] 列表
        """
        measurements = []
        beacon_distances = {}

        for beacon in self.beacons:
            # 获取模拟 RSSI
            rssi = beacon.get_rssi(user_position, environment_factor)

            # 计算距离（使用 RSSI）
            ratio = (beacon.tx_power - rssi) / (10.0 * environment_factor)
            distance = np.power(10, ratio)

            measurements.append((beacon.position, distance))
            beacon_distances[beacon.name] = distance

            print(f"  {beacon.name}: RSSI={rssi:3d}dBm, 估算距离={distance:.2f}m, "
                  f"真实距离={np.linalg.norm(user_position - beacon.position):.2f}m")

        return measurements, beacon_distances

    async def run(self, duration=30, interval=1.0):
        """
        运行模拟

        Args:
            duration: 模拟持续时间（秒）
            interval: 更新间隔（秒）
        """
        print("=" * 70)
        print("iBeacon 模拟测试系统")
        print("=" * 70)
        print(f"模拟时长: {duration}秒")
        print(f"更新间隔: {interval}秒")
        print(f"Beacon 数量: {len(self.beacons)}")
        print("按 Ctrl+C 提前停止")
        print("=" * 70)
        print()

        start_time = time.time()
        iteration = 0

        try:
            while time.time() - start_time < duration:
                iteration += 1
                print(f"\n{'='*70}")
                print(f"第 {iteration} 次迭代 (t={time.time() - start_time:.1f}s)")
                print("-" * 70)

                # 生成模拟位置
                true_position = self.get_simulated_position()
                print(f"🎯 真实位置: X={true_position[0]:.2f}m, Y={true_position[1]:.2f}m, "
                      f"Z={true_position[2]:.2f}m")
                print()

                # 模拟扫描
                measurements, beacon_distances = self.simulate_scan(true_position)
                print()

                # 计算位置（最小二乘）
                estimated_raw = self.position_calculator.least_squares_3d(measurements)

                if estimated_raw is not None:
                    # 卡尔曼滤波
                    estimated_smooth = self.kalman_filter.update(estimated_raw)

                    # 计算误差
                    error = np.linalg.norm(estimated_smooth - true_position)

                    print(f"📍 估算位置: X={estimated_smooth[0]:.2f}m, Y={estimated_smooth[1]:.2f}m, "
                          f"Z={estimated_smooth[2]:.2f}m")
                    print(f"❌ 定位误差: {error:.2f}m")

                    # 更新可视化
                    self.visualizer.update(estimated_smooth, beacon_distances)
                else:
                    print("⚠ 定位失败")

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n接收到中断信号，正在停止...")

        print("\n" + "=" * 70)
        print("模拟完成！")
        print("=" * 70)

        # 保持窗口打开
        input("\n按 Enter 键关闭可视化窗口...")
        self.visualizer.close()


async def main():
    """主函数"""
    system = SimulationSystem()

    try:
        # 运行 30 秒模拟，每秒更新一次
        await system.run(duration=30, interval=1.0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("\n🚀 启动 iBeacon 模拟测试系统...\n")
    asyncio.run(main())
