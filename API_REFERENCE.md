# API 参考文档

## ibeacon_parser.py

### IBeaconData

数据类，存储解析后的 iBeacon 信息。

**属性:**
- `uuid: str` - iBeacon UUID
- `major: int` - Major 值
- `minor: int` - Minor 值
- `tx_power: int` - TxPower（1米处的信号强度，dBm）
- `rssi: int` - 接收信号强度（dBm）

### IBeaconParser

iBeacon 数据解析器。

#### `parse(manufacturer_data: dict, rssi: int) -> Optional[IBeaconData]`

解析 BLE 制造商数据，提取 iBeacon 信息。

**参数:**
- `manufacturer_data: dict` - BLE 制造商数据 `{company_id: bytes}`
- `rssi: int` - 信号强度（dBm）

**返回:**
- `IBeaconData` - 如果是有效的 iBeacon 数据
- `None` - 如果不是 iBeacon 或解析失败

**示例:**
```python
from ibeacon_parser import IBeaconParser

beacon = IBeaconParser.parse(
    manufacturer_data={0x004C: b'\x02\x15...'},
    rssi=-65
)
if beacon:
    print(f"UUID: {beacon.uuid}")
```

---

## ibeacon_scanner.py

### DistanceEstimator

RSSI 距离估算器。

#### `estimate_distance(rssi: int, tx_power: int, n: float = 2.5) -> float`

根据 RSSI 和 TxPower 估算距离。

**参数:**
- `rssi: int` - 当前接收信号强度（dBm）
- `tx_power: int` - 1米处的信号强度（dBm）
- `n: float` - 环境衰减因子（默认 2.5）

**返回:**
- `float` - 估算距离（米），如果 RSSI 无效则返回 -1.0

**公式:**
```
d = 10 ^ ((TxPower - RSSI) / (10 * n))
```

**示例:**
```python
from ibeacon_scanner import DistanceEstimator

estimator = DistanceEstimator()
distance = estimator.estimate_distance(rssi=-65, tx_power=-59, n=2.5)
print(f"距离: {distance:.2f}m")
```

### IBeaconScanner

iBeacon 扫描器。

#### `__init__(environment_factor: float = 2.5)`

初始化扫描器。

**参数:**
- `environment_factor: float` - 环境衰减因子

#### `scan(duration: float = 5.0) -> Dict[tuple, dict]`

扫描 iBeacon 设备。

**参数:**
- `duration: float` - 扫描持续时间（秒）

**返回:**
```python
{
    (uuid, major, minor): {
        'beacon_data': IBeaconData,
        'distance': float,
        'timestamp': float
    },
    ...
}
```

**示例:**
```python
import asyncio
from ibeacon_scanner import IBeaconScanner

async def main():
    scanner = IBeaconScanner(environment_factor=2.5)
    beacons = await scanner.scan(duration=3.0)

    for key, data in beacons.items():
        print(f"{key}: {data['distance']:.2f}m")

asyncio.run(main())
```

#### `scan_continuous(callback: Callable, interval: float = 1.0)`

持续扫描 iBeacon。

**参数:**
- `callback: Callable` - 回调函数 `callback(beacons: Dict)`
- `interval: float` - 扫描间隔（秒）

---

## positioning_3d.py

### Position3D

3D 位置计算器。

#### `trilateration_3d(beacons: List[Tuple[np.ndarray, float]]) -> Optional[np.ndarray]`

使用三边测量计算 3D 位置。

**参数:**
- `beacons: List[Tuple[np.ndarray, float]]` - `[(position, distance), ...]`
  - `position: np.ndarray` - Beacon 位置 `[x, y, z]`
  - `distance: float` - 到 Beacon 的距离（米）

**返回:**
- `np.ndarray` - 估算位置 `[x, y, z]`
- `None` - 如果 Beacon 数量不足（< 3）

#### `least_squares_3d(beacons: List, initial_guess: Optional[np.ndarray] = None) -> Optional[np.ndarray]`

使用最小二乘法优化计算 3D 位置。

**参数:**
- `beacons: List` - 同上
- `initial_guess: Optional[np.ndarray]` - 初始猜测位置，默认为 Beacon 位置平均值

**返回:**
- 同 `trilateration_3d()`

**示例:**
```python
import numpy as np
from positioning_3d import Position3D

calculator = Position3D()

# Beacon 位置和距离
beacons = [
    (np.array([0, 0, 2.5]), 2.3),
    (np.array([5, 0, 2.5]), 3.1),
    (np.array([5, 5, 2.5]), 4.2),
    (np.array([0, 5, 2.5]), 3.5),
]

position = calculator.least_squares_3d(beacons)
print(f"位置: X={position[0]:.2f}, Y={position[1]:.2f}, Z={position[2]:.2f}")
```

#### `filter_outliers(beacons: List, max_distance: float = 50.0) -> List`

过滤异常距离值。

**参数:**
- `beacons: List` - Beacon 列表
- `max_distance: float` - 最大合理距离（米）

**返回:**
- `List` - 过滤后的 Beacon 列表

#### `weighted_position(beacons: List) -> Optional[np.ndarray]`

使用加权平均计算位置（距离越近权重越大）。

### KalmanFilter3D

3D 卡尔曼滤波器。

#### `__init__(process_variance: float = 1e-3, measurement_variance: float = 0.1)`

初始化卡尔曼滤波器。

**参数:**
- `process_variance: float` - 过程噪声方差
- `measurement_variance: float` - 测量噪声方差

#### `update(measured_position: np.ndarray) -> np.ndarray`

更新滤波器并返回平滑后的位置。

**参数:**
- `measured_position: np.ndarray` - 测量得到的位置 `[x, y, z]`

**返回:**
- `np.ndarray` - 滤波后的位置 `[x, y, z]`

**示例:**
```python
import numpy as np
from positioning_3d import KalmanFilter3D

kf = KalmanFilter3D(process_variance=1e-3, measurement_variance=0.5)

# 连续测量
measurements = [
    np.array([2.1, 3.2, 1.5]),
    np.array([2.3, 3.1, 1.6]),
    np.array([2.2, 3.3, 1.4]),
]

for measurement in measurements:
    smoothed = kf.update(measurement)
    print(f"平滑位置: {smoothed}")
```

---

## visualizer_3d.py

### Visualizer3D

3D 实时可视化器。

#### `__init__(beacon_positions: Dict[str, np.ndarray], room_size: tuple = (10, 10, 5))`

初始化可视化器。

**参数:**
- `beacon_positions: Dict[str, np.ndarray]` - `{beacon_name: np.array([x, y, z])}`
- `room_size: tuple` - 房间尺寸 `(width, depth, height)`

#### `update(position: Optional[np.ndarray], beacon_distances: Optional[Dict[str, float]] = None)`

更新可视化。

**参数:**
- `position: Optional[np.ndarray]` - 当前位置 `[x, y, z]`
- `beacon_distances: Optional[Dict[str, float]]` - `{beacon_name: distance}`

**示例:**
```python
import numpy as np
from visualizer_3d import Visualizer3D

# 初始化
beacon_positions = {
    'Beacon-1': np.array([0, 0, 2.5]),
    'Beacon-2': np.array([5, 0, 2.5]),
    'Beacon-3': np.array([5, 5, 2.5]),
    'Beacon-4': np.array([0, 5, 2.5]),
}

viz = Visualizer3D(beacon_positions, room_size=(6, 6, 3))

# 更新位置
current_position = np.array([2.5, 2.5, 1.5])
distances = {'Beacon-1': 2.8, 'Beacon-2': 2.9}

viz.update(current_position, distances)

# 保持窗口打开
viz.show()
```

#### `close()`

关闭可视化窗口。

#### `show()`

显示可视化窗口（阻塞）。

---

## 配置文件格式

### beacon_config.json

```json
{
  "beacons": [
    {
      "uuid": "FDA50693-A4E2-4FB1-AFCF-C6EB07647825",
      "major": 1,
      "minor": 1,
      "position": [0.0, 0.0, 2.5],
      "name": "Beacon-1"
    }
  ],
  "environment_factor": 2.5,
  "scan_interval": 1.0,
  "min_beacons_required": 3,
  "room_size": [6.0, 6.0, 3.5]
}
```

**字段说明:**

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| `beacons` | array | Beacon 列表 | `[{...}, {...}]` |
| `beacons[].uuid` | string | UUID | `"FDA50693-..."` |
| `beacons[].major` | int | Major 值 | `1` |
| `beacons[].minor` | int | Minor 值 | `1` |
| `beacons[].position` | array | 3D 位置 [x,y,z] | `[0, 0, 2.5]` |
| `beacons[].name` | string | 名称 | `"Beacon-1"` |
| `environment_factor` | float | 环境衰减因子 | `2.5` |
| `scan_interval` | float | 扫描间隔（秒） | `1.0` |
| `min_beacons_required` | int | 最少 Beacon 数 | `3` |
| `room_size` | array | 房间尺寸 [W,D,H] | `[6, 6, 3.5]` |

---

## 错误处理

所有主要函数都包含错误处理：

- **解析失败**: `IBeaconParser.parse()` 返回 `None`
- **扫描失败**: 捕获 `bleak` 异常，返回空字典
- **定位失败**: `Position3D` 方法返回 `None`
- **可视化错误**: 自动跳过无效数据

---

## 类型提示

所有函数都包含完整的类型提示，支持静态类型检查：

```python
from typing import Dict, List, Tuple, Optional
import numpy as np
```

使用 mypy 进行类型检查：

```bash
pip install mypy
mypy ibeacon_scanner.py
```

---

## 性能优化建议

1. **降低扫描频率**: 增大 `scan_interval`
2. **限制历史记录**: 修改 `Visualizer3D.max_history`
3. **禁用距离线**: 在 `update()` 中不传 `beacon_distances`
4. **使用更快的优化器**: 在 `least_squares_3d()` 中尝试 `method='Powell'`

---

## 单元测试

运行测试：

```bash
python test_parser.py      # 测试解析器
python test_distance.py    # 测试距离估算
python simulate_test.py    # 端到端模拟测试
```

---

## 贡献指南

欢迎贡献！请遵循：

1. 使用类型提示
2. 添加文档字符串
3. 编写单元测试
4. 遵循 PEP 8 风格
