"""
简化版持续监控工具 - 快速诊断 Beacon 检测问题
"""
import asyncio
from scan_bluetooth_beacons import BluetoothBeaconScanner
import os
from datetime import datetime


async def monitor_beacons(prefix="BeeLinker", duration=30):
    """
    持续监控 Beacon，显示检测统计

    Args:
        prefix: 名称前缀
        duration: 总监控时长（秒）
    """
    print("=" * 80)
    print(f"🔄 开始监控 Beacon（名称前缀: {prefix}）")
    print(f"⏰ 监控时长: {duration} 秒")
    print("=" * 80)
    print()

    detection_stats = {}  # {name: {'detected': count, 'total': count}}
    scan_count = 0
    start_time = datetime.now()

    while (datetime.now() - start_time).total_seconds() < duration:
        scan_count += 1

        print(f"\n{'='*80}")
        print(f"📡 第 {scan_count} 次扫描 - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}\n")

        # 扫描
        scanner = BluetoothBeaconScanner(
            name_prefix=prefix,
            duration=3.0,
            show_all=False
        )

        await scanner.scan()

        # 记录本次检测到的设备
        detected_this_time = set()

        if scanner.devices:
            print(f"✓ 本次检测到 {len(scanner.devices)} 个 Beacon:\n")
            for device in scanner.devices.values():
                if device['is_ibeacon']:
                    name = device['name']
                    detected_this_time.add(name)

                    beacon = device['beacon_data']
                    print(f"  • {name}")
                    print(f"    Major: {beacon.major}, Minor: {beacon.minor}")
                    print(f"    RSSI: {device['rssi']} dBm")
                    print()
        else:
            print("⚠️  本次未检测到任何 Beacon\n")

        # 更新统计
        all_known_beacons = set(detection_stats.keys()) | detected_this_time

        for name in all_known_beacons:
            if name not in detection_stats:
                detection_stats[name] = {'detected': 0, 'total': 0}

            detection_stats[name]['total'] += 1
            if name in detected_this_time:
                detection_stats[name]['detected'] += 1

        # 显示累计统计
        print(f"\n{'─'*80}")
        print("📊 累计检测统计:\n")

        for name in sorted(detection_stats.keys()):
            stats = detection_stats[name]
            rate = (stats['detected'] / stats['total'] * 100) if stats['total'] > 0 else 0

            # 状态标记
            if rate >= 90:
                emoji = "✅"
            elif rate >= 70:
                emoji = "⚠️"
            else:
                emoji = "❌"

            print(f"{emoji} {name}: {stats['detected']}/{stats['total']} ({rate:.1f}%)")

        print(f"{'─'*80}\n")

        # 等待下次扫描
        await asyncio.sleep(2)

    # 最终汇总
    print("\n" + "=" * 80)
    print("📊 最终统计汇总")
    print("=" * 80 + "\n")

    for name in sorted(detection_stats.keys()):
        stats = detection_stats[name]
        rate = (stats['detected'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{name}:")
        print(f"  总扫描: {stats['total']} 次")
        print(f"  检测成功: {stats['detected']} 次")
        print(f"  成功率: {rate:.1f}%")
        print()

    # 建议
    print("=" * 80)
    print("💡 建议:")
    print("=" * 80)

    avg_rate = sum(s['detected']/s['total']*100 for s in detection_stats.values() if s['total']>0) / len(detection_stats) if detection_stats else 0

    if avg_rate >= 90:
        print("✅ 检测稳定性优秀！")
    elif avg_rate >= 70:
        print("⚠️  检测稳定性可接受，建议：")
        print("   1. 将 Beacon 间距增加到 > 0.5 米")
        print("   2. 在 beacon_config.json 中增加 scan_interval 到 3.0")
    else:
        print("❌ 检测稳定性较差，请检查：")
        print("   1. Beacon 电池电量")
        print("   2. 蓝牙是否有其他干扰")
        print("   3. Beacon 是否正常工作（LED 闪烁）")
    print()


if __name__ == '__main__':
    import sys

    prefix = "BeeLinker"
    duration = 30

    if len(sys.argv) > 1:
        prefix = sys.argv[1]
    if len(sys.argv) > 2:
        duration = int(sys.argv[2])

    print(f"\n🚀 启动快速监控")
    print(f"   前缀: {prefix}")
    print(f"   时长: {duration} 秒\n")

    try:
        asyncio.run(monitor_beacons(prefix, duration))
    except KeyboardInterrupt:
        print("\n\n⚠️  监控已中断")
