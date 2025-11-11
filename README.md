# iBeacon 室内 3D 定位系统

一个使用 Python 实现的 iBeacon 室内定位系统，能够实时扫描周围的 iBeacon 设备，计算 3D 位置，并在 3D 可视化窗口中动态展示。

## 功能特性

### 主系统（定位）
- **BLE 扫描**: 使用 `bleak` 库扫描附近的 iBeacon 设备
- **iBeacon 数据解析**: 完整解析 UUID、Major、Minor、TxPower
- **RSSI 距离估算**: 基于对数路径损耗模型估算距离
- **3D 定位算法**: 使用三边测量和最小二乘法优化计算 3D 位置
- **卡尔曼滤波**: 平滑位置估算，减少噪声
- **实时 3D 可视化**: 使用 matplotlib 动态显示位置和 Beacon 分布
- **轨迹追踪**: 实时显示移动轨迹

### 扫描工具（新增）
- **蓝牙设备扫描**: 发现附近所有蓝牙设备
- **名称前缀过滤**: 支持按设备名称前缀搜索
- **信号强度可视化**: 显示 RSSI 信号条
- **自动配置生成**: 一键生成 beacon_config.json
- **结果导出**: 导出 JSON 格式扫描结果

## 系统架构

```
iBeacon/
├── 主系统
│   ├── main.py                    # 主程序入口
│   ├── ibeacon_scanner.py         # BLE 扫描和距离估算
│   ├── ibeacon_parser.py          # iBeacon 数据解析
│   ├── positioning_3d.py          # 3D 定位算法（三边测量、卡尔曼滤波）
│   └── visualizer_3d.py           # 3D 实时可视化
├── 扫描工具
│   └── scan_bluetooth_beacons.py  # 蓝牙扫描工具（支持名称过滤）
├── 测试脚本
│   ├── test_parser.py             # 解析器测试
│   ├── test_distance.py           # 距离估算测试
│   └── simulate_test.py           # 系统模拟测试
├── 配置文件
│   ├── beacon_config.json         # Beacon 位置配置
│   └── requirements.txt           # Python 依赖
└── 文档
    ├── README.md                  # 本文档
    ├── QUICKSTART.md              # 快速开始指南
    ├── SCAN_TOOL_GUIDE.md         # 扫描工具使用指南
    └── API_REFERENCE.md           # API 参考手册
```

## 安装

### 1. 系统要求

- Python 3.8 或更高版本
- 支持 BLE 的系统（macOS、Linux、Windows）
- 蓝牙权限（macOS 需要在系统偏好设置中授权）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括：
- `bleak`: 跨平台 BLE 库
- `numpy`: 数值计算
- `scipy`: 科学计算（优化算法）
- `matplotlib`: 3D 可视化

## 配置

### 快速配置（推荐）

使用扫描工具自动生成配置：

```bash
# 1. 扫描附近的 iBeacon 并生成配置文件
python scan_bluetooth_beacons.py -d 10 -c beacon_config.json

# 2. 编辑生成的文件，填入每个 Beacon 的实际 3D 位置
# 需要使用卷尺或激光测距仪测量

# 3. 运行定位系统
python main.py
```

详细使用说明请参考：[扫描工具使用指南](SCAN_TOOL_GUIDE.md)

### 手动配置

#### beacon_config.json

配置文件定义了 Beacon 的 3D 位置和系统参数：

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

**参数说明**:

- `uuid`: iBeacon 的 UUID（必须与实际 Beacon 匹配）
- `major/minor`: iBeacon 的 Major 和 Minor 值
- `position`: Beacon 在 3D 空间中的坐标 [x, y, z]，单位：米
- `name`: Beacon 名称（用于显示）
- `environment_factor`: 环境衰减因子 n（2~4，室内一般 2.5~3.5）
- `scan_interval`: 扫描间隔（秒）
- `min_beacons_required`: 定位所需的最少 Beacon 数量（至少 3 个）
- `room_size`: 房间尺寸 [宽度, 深度, 高度]，用于可视化

### 部署 Beacon

1. **测量 Beacon 位置**: 使用卷尺或激光测距仪测量每个 Beacon 在房间中的 3D 坐标
2. **记录 Beacon 参数**: 记录每个 Beacon 的 UUID、Major、Minor
3. **更新配置文件**: 将测量的位置和参数填入 `beacon_config.json`

**建议部署方案**:
- 至少 4 个 Beacon（获得更好的 3D 定位）
- Beacon 分布在房间的四个角落
- Beacon 高度一致（如 2.5 米）

## 使用方法

### 1. 启动系统

```bash
python main.py
```

### 2. 程序输出

```
============================================================
iBeacon 室内 3D 定位系统
============================================================
配置的 Beacon 数量: 4
环境衰减因子: 2.5
扫描间隔: 1.0秒
按 Ctrl+C 停止程序
============================================================

============================================================
🔍 正在扫描 iBeacon...
✓ 检测到 3 个 iBeacon:
  Beacon-1: 2.34m (RSSI: -65dBm)
  Beacon-2: 3.12m (RSSI: -70dBm)
  Beacon-3: 4.56m (RSSI: -75dBm)
📍 估算位置: X=2.45m, Y=1.89m, Z=1.20m
```

### 3. 3D 可视化

程序会自动打开一个 3D 可视化窗口，显示：

- **红色三角形**: iBeacon 固定位置
- **蓝色圆点**: 你当前的实时位置
- **蓝色线条**: 你的移动轨迹
- **绿色虚线**: 当前位置到各个 Beacon 的距离（带距离标注）
- **灰色虚线框**: 房间边界

### 4. 停止程序

按 `Ctrl+C` 停止扫描，然后按 `Enter` 关闭可视化窗口。

## 核心算法

### 1. RSSI 距离估算

使用对数路径损耗模型：

```
d = 10 ^ ((TxPower - RSSI) / (10 * n))
```

- `RSSI`: 当前接收信号强度
- `TxPower`: 1 米处的信号强度（从 iBeacon 广播数据获取）
- `n`: 环境衰减因子（2~4，室内一般 2.5~3.5）

### 2. 3D 三边测量定位

已知多个 Beacon 的位置和到这些 Beacon 的距离，使用最小二乘法优化求解当前位置 (x, y, z)：

```python
minimize: Σ [(calculated_distance - measured_distance)²]
```

使用 `scipy.optimize.minimize` 的 Nelder-Mead 算法求解。

### 3. 卡尔曼滤波平滑

使用简单的 3D 卡尔曼滤波器平滑位置估算，减少 RSSI 波动带来的噪声：

- **预测步骤**: 基于上一次位置预测当前位置
- **更新步骤**: 融合测量值更新估计

## 故障排除

### 1. 未检测到 iBeacon

**可能原因**:
- 蓝牙未开启
- Beacon 距离过远或电量不足
- UUID/Major/Minor 配置不匹配
- 系统蓝牙权限未授权

**解决方法**:
- 检查蓝牙是否开启
- 确认 Beacon 正常工作（LED 闪烁）
- 验证配置文件中的 UUID、Major、Minor 与实际 Beacon 一致
- 在系统设置中授予 Python 蓝牙权限（macOS）

### 2. 定位不准确

**可能原因**:
- 环境衰减因子 `n` 设置不合适
- Beacon 位置配置不准确
- 环境中存在多路径效应或障碍物
- 检测到的 Beacon 数量不足

**解决方法**:
- 调整 `environment_factor` 参数（尝试 2.0~4.0）
- 重新测量并更新 Beacon 位置
- 在开阔空间测试，避免金属物体干扰
- 增加 Beacon 数量（至少 4 个）

### 3. 可视化窗口无响应

**可能原因**:
- matplotlib 后端问题
- 系统图形界面不兼容

**解决方法**:
- 尝试更换 matplotlib 后端（在 `visualizer_3d.py` 开头添加）:
  ```python
  import matplotlib
  matplotlib.use('TkAgg')  # 或 'Qt5Agg'
  ```

## 技术栈

- **BLE 扫描**: `bleak`
- **数据解析**: 手动解析 iBeacon 格式（struct）
- **距离估算**: 对数路径损耗模型
- **定位算法**: 三边测量 / 最小二乘优化（scipy）
- **平滑滤波**: 卡尔曼滤波
- **3D 可视化**: `matplotlib` 3D 绘图

## 性能优化建议

1. **增加 Beacon 数量**: 至少 4 个 Beacon，分布均匀
2. **调整环境因子**: 根据实际环境调整 `environment_factor`
3. **异常值过滤**: 系统已内置距离过滤（最大 50 米）
4. **降低扫描频率**: 如果性能不足，可增大 `scan_interval`

## 扩展功能

可以考虑的扩展：

- **数据记录**: 保存位置轨迹到文件
- **Web 界面**: 使用 Flask + plotly 实现 Web 实时可视化
- **多用户**: 支持多个设备同时定位
- **室内地图**: 叠加室内地图到可视化
- **楼层切换**: 支持多楼层定位

## 参考资料

- [iBeacon 技术规范](https://developer.apple.com/ibeacon/)
- [Bleak 文档](https://bleak.readthedocs.io/)
- [RSSI 距离估算模型](https://en.wikipedia.org/wiki/Log-distance_path_loss_model)
- [三边测量算法](https://en.wikipedia.org/wiki/Trilateration)

## 许可证

MIT License

## 作者

Created with Claude Code
