"""
蓝牙信标扫描工具
支持扫描附近的所有蓝牙设备，并可按名称前缀过滤
"""
import asyncio
from bleak import BleakScanner
from ibeacon_parser import IBeaconParser
import argparse
from datetime import datetime
import json


class BluetoothBeaconScanner:
    """蓝牙信标扫描器"""

    def __init__(self, name_prefix=None, duration=10.0, show_all=False):
        """
        初始化扫描器

        Args:
            name_prefix: 设备名称前缀过滤（如 "Beacon"）
            duration: 扫描持续时间（秒）
            show_all: 是否显示所有蓝牙设备（包括非iBeacon）
        """
        self.name_prefix = name_prefix
        self.duration = duration
        self.show_all = show_all
        self.devices = {}

    def _match_prefix(self, name):
        """
        检查设备名称是否匹配前缀

        Args:
            name: 设备名称

        Returns:
            bool: 是否匹配
        """
        if not self.name_prefix:
            return True
        if not name:
            return False
        return name.startswith(self.name_prefix)

    def _format_rssi_bar(self, rssi):
        """
        将 RSSI 转换为信号强度条

        Args:
            rssi: 信号强度

        Returns:
            str: 信号强度条
        """
        if rssi >= -50:
            return "████████" + " (极强)"
        elif rssi >= -60:
            return "██████  " + " (强)"
        elif rssi >= -70:
            return "████    " + " (中)"
        elif rssi >= -80:
            return "██      " + " (弱)"
        else:
            return "▌       " + " (很弱)"

    async def scan(self):
        """扫描蓝牙设备"""
        print("=" * 80)
        print(f"🔍 蓝牙信标扫描工具")
        print("=" * 80)
        print(f"扫描时长: {self.duration} 秒")
        if self.name_prefix:
            print(f"名称过滤: 前缀 = '{self.name_prefix}'")
        if self.show_all:
            print(f"模式: 显示所有蓝牙设备")
        else:
            print(f"模式: 仅显示 iBeacon 设备")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        print("⏳ 正在扫描...")
        print()

        def detection_callback(device, advertisement_data):
            """设备检测回调"""
            # 检查名称前缀
            if not self._match_prefix(device.name):
                return

            # 尝试解析 iBeacon 数据
            beacon_data = IBeaconParser.parse(
                advertisement_data.manufacturer_data,
                advertisement_data.rssi
            )

            # 如果不是 iBeacon 且只显示 iBeacon，则跳过
            if not self.show_all and not beacon_data:
                return

            # 存储设备信息
            device_key = device.address
            self.devices[device_key] = {
                'address': device.address,
                'name': device.name or "(未命名)",
                'rssi': advertisement_data.rssi,
                'beacon_data': beacon_data,
                'is_ibeacon': beacon_data is not None,
                'last_seen': datetime.now()
            }

        # 执行扫描
        scanner = BleakScanner(detection_callback=detection_callback)
        await scanner.start()
        await asyncio.sleep(self.duration)
        await scanner.stop()

        print(f"\n✓ 扫描完成！共发现 {len(self.devices)} 个设备")
        print()

    def display_results(self):
        """显示扫描结果"""
        if not self.devices:
            print("⚠ 未发现任何设备")
            return

        # 按 RSSI 排序（信号强度从高到低）
        sorted_devices = sorted(
            self.devices.values(),
            key=lambda x: x['rssi'],
            reverse=True
        )

        print("=" * 80)
        print("📱 扫描结果")
        print("=" * 80)
        print()

        # 分组显示：iBeacon 和其他设备
        ibeacons = [d for d in sorted_devices if d['is_ibeacon']]
        others = [d for d in sorted_devices if not d['is_ibeacon']]

        if ibeacons:
            print(f"🔶 iBeacon 设备 ({len(ibeacons)} 个)")
            print("-" * 80)
            for i, device in enumerate(ibeacons, 1):
                self._display_ibeacon(i, device)
            print()

        if others and self.show_all:
            print(f"📡 其他蓝牙设备 ({len(others)} 个)")
            print("-" * 80)
            for i, device in enumerate(others, 1):
                self._display_device(i, device)
            print()

    def _display_ibeacon(self, index, device):
        """显示 iBeacon 设备信息"""
        beacon = device['beacon_data']
        print(f"{index}. {device['name']}")
        print(f"   地址: {device['address']}")
        print(f"   UUID: {beacon.uuid}")
        print(f"   Major: {beacon.major}")
        print(f"   Minor: {beacon.minor}")
        print(f"   TxPower: {beacon.tx_power} dBm")
        print(f"   RSSI: {device['rssi']} dBm  {self._format_rssi_bar(device['rssi'])}")
        print(f"   最后更新: {device['last_seen'].strftime('%H:%M:%S')}")
        print()

    def _display_device(self, index, device):
        """显示普通蓝牙设备信息"""
        print(f"{index}. {device['name']}")
        print(f"   地址: {device['address']}")
        print(f"   RSSI: {device['rssi']} dBm  {self._format_rssi_bar(device['rssi'])}")
        print(f"   最后更新: {device['last_seen'].strftime('%H:%M:%S')}")
        print()

    def export_to_json(self, filename="scan_results.json"):
        """
        导出扫描结果为 JSON 文件

        Args:
            filename: 输出文件名
        """
        if not self.devices:
            print("⚠ 没有数据可导出")
            return

        # 准备导出数据
        export_data = {
            'scan_time': datetime.now().isoformat(),
            'total_devices': len(self.devices),
            'devices': []
        }

        for device in self.devices.values():
            device_info = {
                'address': device['address'],
                'name': device['name'],
                'rssi': device['rssi'],
                'is_ibeacon': device['is_ibeacon']
            }

            if device['is_ibeacon']:
                beacon = device['beacon_data']
                device_info['ibeacon'] = {
                    'uuid': beacon.uuid,
                    'major': beacon.major,
                    'minor': beacon.minor,
                    'tx_power': beacon.tx_power
                }

            export_data['devices'].append(device_info)

        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✓ 扫描结果已导出到: {filename}")

    def export_beacon_config(self, filename="discovered_beacons.json"):
        """
        导出为 beacon_config.json 格式（可直接用于定位系统）

        Args:
            filename: 输出文件名
        """
        # 只导出 iBeacon
        ibeacons = [d for d in self.devices.values() if d['is_ibeacon']]

        if not ibeacons:
            print("⚠ 没有发现 iBeacon 设备，无法导出配置")
            return

        config = {
            "beacons": [],
            "environment_factor": 2.5,
            "scan_interval": 1.0,
            "min_beacons_required": 3,
            "room_size": [10.0, 10.0, 3.5]
        }

        for i, device in enumerate(ibeacons, 1):
            beacon = device['beacon_data']
            config['beacons'].append({
                "uuid": beacon.uuid,
                "major": beacon.major,
                "minor": beacon.minor,
                "position": [0.0, 0.0, 2.5],  # 需要手动测量
                "name": device['name']
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✓ Beacon 配置已导出到: {filename}")
        print(f"⚠ 请手动编辑文件，填入每个 Beacon 的实际 3D 位置坐标")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='蓝牙信标扫描工具 - 扫描附近的蓝牙设备和 iBeacon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 扫描所有 iBeacon（默认 10 秒）
  python scan_bluetooth_beacons.py

  # 扫描所有蓝牙设备（包括非 iBeacon）
  python scan_bluetooth_beacons.py --all

  # 扫描名称以 "Beacon" 开头的设备
  python scan_bluetooth_beacons.py --prefix Beacon

  # 扫描 20 秒
  python scan_bluetooth_beacons.py --duration 20

  # 扫描并导出为 JSON
  python scan_bluetooth_beacons.py --export results.json

  # 扫描并生成 beacon_config.json
  python scan_bluetooth_beacons.py --config my_beacons.json
        """
    )

    parser.add_argument(
        '-p', '--prefix',
        type=str,
        help='设备名称前缀过滤（如: Beacon, Apple, iBeacon）'
    )

    parser.add_argument(
        '-d', '--duration',
        type=float,
        default=10.0,
        help='扫描持续时间（秒），默认 10 秒'
    )

    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='显示所有蓝牙设备（包括非 iBeacon）'
    )

    parser.add_argument(
        '-e', '--export',
        type=str,
        metavar='FILE',
        help='导出扫描结果为 JSON 文件'
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        metavar='FILE',
        help='导出为 beacon_config.json 格式'
    )

    args = parser.parse_args()

    # 创建扫描器
    scanner = BluetoothBeaconScanner(
        name_prefix=args.prefix,
        duration=args.duration,
        show_all=args.all
    )

    try:
        # 执行扫描
        await scanner.scan()

        # 显示结果
        scanner.display_results()

        # 导出文件
        if args.export:
            scanner.export_to_json(args.export)

        if args.config:
            scanner.export_beacon_config(args.config)

    except KeyboardInterrupt:
        print("\n\n⚠ 扫描已中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
