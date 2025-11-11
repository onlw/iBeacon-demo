"""
测试 iBeacon 数据解析功能
"""
from ibeacon_parser import IBeaconParser


def test_ibeacon_parser():
    """测试 iBeacon 解析器"""
    print("=" * 60)
    print("iBeacon 数据解析器测试")
    print("=" * 60)

    # 模拟 iBeacon 广播数据
    # 格式: 0x02 0x15 + UUID(16字节) + Major(2字节) + Minor(2字节) + TxPower(1字节)

    # 示例 UUID: FDA50693-A4E2-4FB1-AFCF-C6EB07647825
    uuid_bytes = bytes.fromhex('FDA50693A4E24FB1AFCFC6EB07647825')
    major = 1
    minor = 2
    tx_power = -59

    # 构造 iBeacon 数据
    ibeacon_data = bytes([0x02, 0x15]) + uuid_bytes
    ibeacon_data += major.to_bytes(2, 'big')
    ibeacon_data += minor.to_bytes(2, 'big')
    ibeacon_data += tx_power.to_bytes(1, 'big', signed=True)

    # 构造制造商数据
    manufacturer_data = {0x004C: ibeacon_data}

    # 解析
    result = IBeaconParser.parse(manufacturer_data, rssi=-65)

    if result:
        print(f"✓ 解析成功!")
        print(f"  UUID: {result.uuid}")
        print(f"  Major: {result.major}")
        print(f"  Minor: {result.minor}")
        print(f"  TxPower: {result.tx_power}dBm")
        print(f"  RSSI: {result.rssi}dBm")
        print()
        print(f"完整信息: {result}")
    else:
        print("✗ 解析失败")

    print("=" * 60)


if __name__ == '__main__':
    test_ibeacon_parser()
