"""
单个 iBeacon 距离测量程序
实时扫描单个 iBeacon 并计算距离
"""
import asyncio
import math
from bleak import BleakScanner
from ibeacon_parser import IBeaconParser
from typing import Optional
from datetime import datetime


class SingleBeaconDistance:
    """单个 iBeacon 距离计算器"""

    def __init__(self, environment_factor: float = 2.5):
        """
        初始化距离计算器

        Args:
            environment_factor: 环境衰减因子 (室内: 2.5-3.5, 开放空间: 2.0-2.5)
        """
        self.environment_factor = environment_factor
        self.target_beacon = None  # 目标 beacon 标识
        self.last_distance = None
        self.distance_history = []  # 历史距离记录

    def calculate_distance(self, rssi: int, tx_power: int) -> float:
        """
        根据 RSSI 和 TxPower 计算距离

        使用改进的路径损耗模型：d = 10 ^ ((TxPower - RSSI) / (10 * n))
        并进行分段校准以提高精度

        Args:
            rssi: 接收信号强度指示 (dBm)
            tx_power: 发射功率 (1米处的信号强度, dBm)

        Returns:
            估算距离 (米)
        """
        if rssi == 0:
            return -1.0

        # 基础路径损耗模型
        ratio = (tx_power - rssi) / (10.0 * self.environment_factor)
        distance = math.pow(10, ratio)

        return distance

    def get_distance_category(self, distance: float) -> str:
        """
        根据距离返回分类描述

        Args:
            distance: 距离 (米)

        Returns:
            距离分类描述
        """
        if distance < 0:
            return "未知"
        elif distance < 0.5:
            return "紧邻 (Immediate)"
        elif distance < 2.0:
            return "近距离 (Near)"
        elif distance < 5.0:
            return "中距离 (Medium)"
        elif distance < 10.0:
            return "远距离 (Far)"
        else:
            return "很远 (Very Far)"

    def add_to_history(self, distance: float, max_history: int = 10):
        """
        添加距离到历史记录并返回平滑后的距离

        Args:
            distance: 当前距离
            max_history: 最大历史记录数

        Returns:
            平滑后的距离
        """
        self.distance_history.append(distance)
        if len(self.distance_history) > max_history:
            self.distance_history.pop(0)

        # 返回移动平均
        return sum(self.distance_history) / len(self.distance_history)

    async def scan_single_beacon(self,
                                 target_uuid: Optional[str] = None,
                                 target_major: Optional[int] = None,
                                 target_minor: Optional[int] = None,
                                 duration: float = 10.0,
                                 continuous: bool = False):
        """
        扫描单个 iBeacon 并显示距离

        Args:
            target_uuid: 目标 beacon UUID (None 表示扫描第一个检测到的)
            target_major: 目标 beacon Major 值
            target_minor: 目标 beacon Minor 值
            duration: 每次扫描持续时间 (秒)
            continuous: 是否持续扫描
        """
        print("=" * 70)
        print("单个 iBeacon 距离测量程序")
        print("=" * 70)
        if target_uuid:
            print(f"目标 UUID: {target_uuid}")
            if target_major is not None:
                print(f"目标 Major: {target_major}")
            if target_minor is not None:
                print(f"目标 Minor: {target_minor}")
        else:
            print("模式: 扫描第一个检测到的 iBeacon")
        print(f"环境衰减因子: {self.environment_factor}")
        print("按 Ctrl+C 停止扫描")
        print("=" * 70)
        print()

        beacon_found = False
        scan_count = 0

        try:
            while True:
                scan_count += 1
                print(f"\n[扫描 #{scan_count}] {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 70)

                # 临时存储本次扫描结果
                current_beacon = None

                def detection_callback(device, advertisement_data):
                    nonlocal current_beacon, beacon_found

                    # 解析 iBeacon
                    beacon_data = IBeaconParser.parse(
                        advertisement_data.manufacturer_data,
                        advertisement_data.rssi
                    )

                    if beacon_data:
                        # 检查是否匹配目标 beacon
                        if target_uuid and beacon_data.uuid != target_uuid:
                            return
                        if target_major is not None and beacon_data.major != target_major:
                            return
                        if target_minor is not None and beacon_data.minor != target_minor:
                            return
                        print(f"检测到 iBeacon: {beacon_data.uuid}")
                        # 如果没有指定目标，使用第一个检测到的
                        if not self.target_beacon:
                            self.target_beacon = (beacon_data.uuid, beacon_data.major, beacon_data.minor)
                            print(f"\n✓ 锁定目标 iBeacon:")
                            print(f"  UUID: {beacon_data.uuid}")
                            print(f"  Major: {beacon_data.major}")
                            print(f"  Minor: {beacon_data.minor}")
                            print()

                        # 检查是否是我们的目标 beacon
                        if self.target_beacon == (beacon_data.uuid, beacon_data.major, beacon_data.minor):
                            current_beacon = beacon_data
                            beacon_found = True

                # 执行扫描
                scanner = BleakScanner(detection_callback=detection_callback)
                await scanner.start()
                await asyncio.sleep(duration)
                await scanner.stop()

                # 处理扫描结果
                if current_beacon:
                    # 计算距离
                    distance = self.calculate_distance(
                        current_beacon.rssi,
                        current_beacon.tx_power
                    )

                    # 平滑距离
                    smoothed_distance = self.add_to_history(distance)

                    # 显示结果
                    category = self.get_distance_category(smoothed_distance)

                    print(f"📡 RSSI: {current_beacon.rssi} dBm")
                    print(f"📶 TxPower: {current_beacon.tx_power} dBm")
                    print(f"📏 原始距离: {distance:.2f} 米")
                    print(f"📏 平滑距离: {smoothed_distance:.2f} 米")
                    print(f"📍 距离分类: {category}")

                    # 显示变化趋势
                    if self.last_distance is not None:
                        change = smoothed_distance - self.last_distance
                        if abs(change) > 0.1:
                            trend = "📈 远离" if change > 0 else "📉 靠近"
                            print(f"{trend} (变化: {abs(change):.2f}m)")

                    self.last_distance = smoothed_distance

                else:
                    if beacon_found:
                        print("⚠ 信号丢失")
                    else:
                        print("⚠ 未检测到目标 iBeacon")

                # 如果不是持续模式，扫描一次后退出
                if not continuous:
                    break

                # 短暂暂停
                await asyncio.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\n程序已停止")


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='单个 iBeacon 距离测量')
    parser.add_argument('--uuid', type=str, help='目标 iBeacon UUID')
    parser.add_argument('--major', type=int, help='目标 iBeacon Major 值')
    parser.add_argument('--minor', type=int, help='目标 iBeacon Minor 值')
    parser.add_argument('--env-factor', type=float, default=3.0,
                       help='环境衰减因子 (默认: 3.0)')
    parser.add_argument('--duration', type=float, default=2.0,
                       help='扫描持续时间/秒 (默认: 2.0)')
    parser.add_argument('--continuous', action='store_true',
                       help='持续扫描模式')

    args = parser.parse_args()

    # 创建距离计算器
    calculator = SingleBeaconDistance(environment_factor=args.env_factor)

    # 开始扫描
    await calculator.scan_single_beacon(
        target_uuid=args.uuid,
        target_major=args.major,
        target_minor=args.minor,
        duration=args.duration,
        continuous=args.continuous
    )


if __name__ == '__main__':
    asyncio.run(main())
