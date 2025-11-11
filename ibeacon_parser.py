"""
iBeacon 数据解析模块
解析 BLE 广播数据中的 iBeacon 格式信息
"""
import struct
from dataclasses import dataclass
from typing import Optional


@dataclass
class IBeaconData:
    """iBeacon 数据结构"""
    uuid: str
    major: int
    minor: int
    tx_power: int
    rssi: int

    def __str__(self):
        return (f"UUID: {self.uuid}, Major: {self.major}, Minor: {self.minor}, "
                f"TxPower: {self.tx_power}dBm, RSSI: {self.rssi}dBm")


class IBeaconParser:
    """iBeacon 数据解析器"""

    # Apple 公司 ID
    APPLE_COMPANY_ID = 0x004C
    # iBeacon 类型标识
    IBEACON_TYPE = 0x02
    IBEACON_LENGTH = 0x15

    @staticmethod
    def parse(manufacturer_data: dict, rssi: int) -> Optional[IBeaconData]:
        """
        解析 iBeacon 数据

        Args:
            manufacturer_data: BLE 制造商数据字典 {company_id: bytes}
            rssi: 信号强度

        Returns:
            IBeaconData 对象，如果不是 iBeacon 数据则返回 None
        """
        # 检查是否包含 Apple 公司数据
        if IBeaconParser.APPLE_COMPANY_ID not in manufacturer_data:
            return None

        data = manufacturer_data[IBeaconParser.APPLE_COMPANY_ID]

        # iBeacon 数据格式验证
        # 最小长度：2字节(type+length) + 16字节(UUID) + 2字节(Major) + 2字节(Minor) + 1字节(TxPower) = 23字节
        if len(data) < 23:
            return None


        # 检查 iBeacon 类型标识
        if data[0] != IBeaconParser.IBEACON_TYPE or data[1] != IBeaconParser.IBEACON_LENGTH:
            return None

        try:
            # 解析 UUID (16 字节，从索引 2 开始)
            uuid_bytes = data[2:18]
            uuid = '-'.join([
                uuid_bytes[0:4].hex().upper(),
                uuid_bytes[4:6].hex().upper(),
                uuid_bytes[6:8].hex().upper(),
                uuid_bytes[8:10].hex().upper(),
                uuid_bytes[10:16].hex().upper()
            ])
            
            # 解析 Major (2 字节，大端序)
            major = struct.unpack('>H', data[18:20])[0]

            # 解析 Minor (2 字节，大端序)
            minor = struct.unpack('>H', data[20:22])[0]

            # 解析 TxPower (1 字节，有符号整数)
            tx_power = struct.unpack('b', data[22:23])[0]

            return IBeaconData(
                uuid=uuid,
                major=major,
                minor=minor,
                tx_power=tx_power,
                rssi=rssi
            )
        except Exception as e:
            print(f"解析 iBeacon 数据时出错: {e}")
            return None
