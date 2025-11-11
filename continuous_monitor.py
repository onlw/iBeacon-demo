"""
持续监控 Beacon 检测稳定性
解决 Beacon 检测时有时无的问题
"""
import asyncio
from ibeacon_scanner import IBeaconScanner
from ibeacon_parser import IBeaconParser
import os
from datetime import datetime
import argparse


class BeaconMonitor:
    """Beacon 持续监控器"""

    def __init__(self, name_prefix=None, scan_duration=3.0, interval=2.0):
        """
        初始化监控器

        Args:
            name_prefix: 设备名称前缀过滤
            scan_duration: 每次扫描时长（秒）
            interval: 扫描间隔（秒）
        """
        self.name_prefix = name_prefix
        self.scan_duration = scan_duration
        self.interval = interval
        self.scanner = IBeaconScanner(environment_factor=2.5)

        self.scan_count = 0
        self.detection_history = {}  # {beacon_key: {'name': ..., 'history': [...]}}
        self.last_seen = {}  # {beacon_key: timestamp}

    def _match_prefix(self, name):
        """检查名称是否匹配前缀"""
        if not self.name_prefix:
            return True
        if not name:
            return False
        return name.startswith(self.name_prefix)

    def _get_beacon_key(self, beacon_data):
        """生成 Beacon 唯一标识"""
        return f"{beacon_data.uuid}-{beacon_data.major}-{beacon_data.minor}"

    async def scan_once(self):
        """执行一次扫描"""
        beacons = await self.scanner.scan(duration=self.scan_duration)

        detected_keys = set()
        current_beacons = []

        for key, data in beacons.items():
            beacon_data = data['beacon_data']
            beacon_key = self._get_beacon_key(beacon_data)

            # 获取设备名称（从 key 或使用默认）
            name = f"{beacon_data.major}-{beacon_data.minor}"
            if hasattr(beacon_data, 'name'):
                name = beacon_data.name

            # 名称过滤
            if not self._match_prefix(name):
                continue

            detected_keys.add(beacon_key)

            # 初始化历史记录
            if beacon_key not in self.detection_history:
                self.detection_history[beacon_key] = {
                    'name': name,
                    'uuid': beacon_data.uuid,
                    'major': beacon_data.major,
                    'minor': beacon_data.minor,
                    'history': []
                }

            # 记录检测成功
            self.detection_history[beacon_key]['history'].append(True)
            self.last_seen[beacon_key] = datetime.now()

            # 保存当前检测到的设备
            current_beacons.append({
                'key': beacon_key,
                'name': name,
                'rssi': beacon_data.rssi,
                'distance': data['distance'],
                'tx_power': beacon_data.tx_power
            })

        # 标记未检测到的 Beacon
        for beacon_key in self.detection_history:
            if beacon_key not in detected_keys:
                self.detection_history[beacon_key]['history'].append(False)

        return current_beacons

    def display_statistics(self, current_beacons):
        """显示统计信息"""
        # 清屏
        os.system('clear' if os.name != 'nt' else 'cls')

        self.scan_count += 1

        print("=" * 80)
        print(f"🔄 Beacon 持续监控 - 第 {self.scan_count} 次扫描")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.name_prefix:
            print(f"🔍 过滤: 名称前缀 = '{self.name_prefix}'")
        print("=" * 80)
        print()

        # 显示检测统计
        if self.detection_history:
            print("📊 检测统计（所有发现过的 Beacon）:")
            print("-" * 80)

            for beacon_key, info in sorted(self.detection_history.items(),
                                          key=lambda x: sum(x[1]['history']),
                                          reverse=True):
                history = info['history']
                detected = sum(history)
                total = len(history)
                rate = (detected / total) * 100

                # 最近 20 次的状态
                recent = history[-20:]
                status = ''.join(['✓' if x else '✗' for x in recent])

                # 最后检测时间
                last_seen_str = "从未"
                if beacon_key in self.last_seen:
                    seconds_ago = (datetime.now() - self.last_seen[beacon_key]).total_seconds()
                    if seconds_ago < 60:
                        last_seen_str = f"{int(seconds_ago)}秒前"
                    else:
                        last_seen_str = f"{int(seconds_ago/60)}分钟前"

                # 颜色标记
                if rate >= 90:
                    status_emoji = "✅"
                elif rate >= 70:
                    status_emoji = "⚠️"
                else:
                    status_emoji = "❌"

                print(f"{status_emoji} {info['name']} (Major:{info['major']}, Minor:{info['minor']})")
                print(f"   检测率: {detected}/{total} ({rate:.1f}%)")
                print(f"   最后检测: {last_seen_str}")
                print(f"   最近{len(recent)}次: {status}")
                print()
        else:
            print("⚠️  尚未检测到任何 Beacon")
            print()

        # 显示当前检测到的设备
        print("🔶 当前扫描结果:")
        print("-" * 80)
        if current_beacons:
            for i, beacon in enumerate(current_beacons, 1):
                signal_bar = self._get_signal_bar(beacon['rssi'])
                print(f"{i}. {beacon['name']}")
                print(f"   RSSI: {beacon['rssi']} dBm {signal_bar}")
                print(f"   距离: {beacon['distance']:.2f}m")
                print(f"   TxPower: {beacon['tx_power']} dBm")
                print()
        else:
            print("⚠️  本次扫描未检测到任何 Beacon")
            print()

        # 显示建议
        self._show_recommendations()

        print()
        print("按 Ctrl+C 停止监控")
        print("=" * 80)

    def _get_signal_bar(self, rssi):
        """获取信号强度条"""
        if rssi >= -50:
            return "████████ (极强)"
        elif rssi >= -60:
            return "██████   (强)"
        elif rssi >= -70:
            return "████     (中)"
        elif rssi >= -80:
            return "██       (弱)"
        else:
            return "▌        (很弱)"

    def _show_recommendations(self):
        """显示优化建议"""
        if not self.detection_history:
            return

        print("💡 优化建议:")
        print("-" * 80)

        # 计算整体检测率
        total_rate = 0
        for info in self.detection_history.values():
            if info['history']:
                rate = sum(info['history']) / len(info['history']) * 100
                total_rate += rate

        avg_rate = total_rate / len(self.detection_history) if self.detection_history else 0

        if avg_rate >= 90:
            print("✅ 检测稳定性优秀，系统工作正常！")
        elif avg_rate >= 70:
            print("⚠️  检测稳定性可接受，但建议优化：")
            print("   • 增加扫描时长（当前 {:.1f}秒）".format(self.scan_duration))
            print("   • 将 Beacon 分开放置（间距 > 0.5米）")
        else:
            print("❌ 检测稳定性较差，请检查：")
            print("   • Beacon 电池是否充足")
            print("   • 是否有强烈信号干扰")
            print("   • Beacon 是否正常工作（LED 闪烁）")
            print("   • 蓝牙权限是否正常")

    async def run(self):
        """运行持续监控"""
        print("=" * 80)
        print("🚀 启动 Beacon 持续监控")
        print("=" * 80)
        print(f"扫描时长: {self.scan_duration} 秒")
        print(f"扫描间隔: {self.interval} 秒")
        if self.name_prefix:
            print(f"名称过滤: '{self.name_prefix}'")
        print()
        print("正在启动...")
        await asyncio.sleep(1)

        try:
            while True:
                # 执行扫描
                current_beacons = await self.scan_once()

                # 显示统计
                self.display_statistics(current_beacons)

                # 等待下次扫描
                await asyncio.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 80)
            print("✓ 监控已停止")
            print("=" * 80)
            self._show_final_summary()

    def _show_final_summary(self):
        """显示最终汇总"""
        if not self.detection_history:
            return

        print()
        print("📊 最终统计汇总:")
        print("-" * 80)

        for beacon_key, info in sorted(self.detection_history.items()):
            history = info['history']
            detected = sum(history)
            total = len(history)
            rate = (detected / total) * 100 if total > 0 else 0

            print(f"{info['name']}:")
            print(f"  总扫描次数: {total}")
            print(f"  检测成功次数: {detected}")
            print(f"  检测成功率: {rate:.1f}%")
            print()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Beacon 持续监控工具 - 诊断检测稳定性问题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 监控所有 Beacon
  python continuous_monitor.py

  # 监控名称以 "BeeLinker" 开头的 Beacon
  python continuous_monitor.py --prefix BeeLinker

  # 自定义扫描参数
  python continuous_monitor.py --scan 5 --interval 3
        """
    )

    parser.add_argument(
        '-p', '--prefix',
        type=str,
        help='设备名称前缀过滤'
    )

    parser.add_argument(
        '-s', '--scan',
        type=float,
        default=3.0,
        help='每次扫描时长（秒），默认 3.0'
    )

    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=2.0,
        help='扫描间隔（秒），默认 2.0'
    )

    args = parser.parse_args()

    monitor = BeaconMonitor(
        name_prefix=args.prefix,
        scan_duration=args.scan,
        interval=args.interval
    )

    await monitor.run()


if __name__ == '__main__':
    asyncio.run(main())
