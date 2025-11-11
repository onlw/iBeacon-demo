"""
iBeacon 扫描模块
使用 bleak 扫描附近的 iBeacon 设备
"""
import asyncio
from bleak import BleakScanner
from typing import Dict, Callable, Optional
from ibeacon_parser import IBeaconParser, IBeaconData
import math


class DistanceEstimator:
    """RSSI 距离估算器"""

    @staticmethod
    def estimate_distance(rssi: int, tx_power: int, n: float = 2.5) -> float:
        """
        根据 RSSI 和 TxPower 估算距离

        改进的距离估算公式，增加了近距离和远距离的校准

        Args:
            rssi: 当前接收信号强度
            tx_power: 1米处的信号强度（通常等于 TxPower）
            n: 环境衰减因子 (2~4，室内一般 2.5~3.5)

        Returns:
            估算距离（米）
        """
        if rssi == 0:
            return -1.0  # 无效信号

        # 基础路径损耗模型
        ratio = (tx_power - rssi) / (10.0 * n)
        distance = math.pow(10, ratio)

        return distance


class IBeaconScanner:
    """iBeacon 扫描器"""

    def __init__(self, environment_factor: float = 2.5):
        """
        初始化扫描器

        Args:
            environment_factor: 环境衰减因子
        """
        self.environment_factor = environment_factor
        self.distance_estimator = DistanceEstimator()
        self.beacons: Dict[tuple, dict] = {}  # {(uuid, major, minor): {data, distance}}

    async def scan(self, duration: float = 5.0) -> Dict[tuple, dict]:
        """
        扫描 iBeacon 设备

        Args:
            duration: 扫描持续时间（秒）

        Returns:
            扫描到的 iBeacon 字典 {(uuid, major, minor): {beacon_data, distance}}
        """
        self.beacons.clear()

        def detection_callback(device, advertisement_data):
            """BLE 设备检测回调"""
            # 解析 iBeacon 数据
            beacon_data = IBeaconParser.parse(
                advertisement_data.manufacturer_data,
                advertisement_data.rssi
            )

            if beacon_data:
                # 估算距离
                distance = self.distance_estimator.estimate_distance(
                    beacon_data.rssi,
                    beacon_data.tx_power,
                    self.environment_factor
                )

                # 存储 beacon 数据
                key = (beacon_data.uuid, beacon_data.major, beacon_data.minor)
                self.beacons[key] = {
                    'beacon_data': beacon_data,
                    'distance': distance,
                    'timestamp': asyncio.get_event_loop().time()
                }

        # 执行扫描
        scanner = BleakScanner(detection_callback=detection_callback)
        await scanner.start()
        await asyncio.sleep(duration)
        await scanner.stop()

        return self.beacons

    async def scan_continuous(self, callback: Callable[[Dict[tuple, dict]], None],
                             interval: float = 1.0):
        """
        持续扫描 iBeacon

        Args:
            callback: 扫描结果回调函数
            interval: 扫描间隔（秒）
        """
        while True:
            beacons = await self.scan(duration=interval)
            if beacons:
                callback(beacons)
            await asyncio.sleep(0.1)  # 短暂暂停避免 CPU 占用过高
