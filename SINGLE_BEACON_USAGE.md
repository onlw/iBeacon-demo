# 单个 iBeacon 距离测量工具使用说明

本项目提供了两个工具来测量单个 iBeacon 设备的距离：

## 工具列表

### 1. `single_beacon_distance.py` - 基础距离测量工具
简单的命令行工具，用于测量单个 iBeacon 的距离。

### 2. `realtime_distance_monitor.py` - 实时距离监控工具
带有实时图表可视化的距离监控工具，可以看到距离和 RSSI 的变化趋势。

---

## 1. 基础距离测量工具

### 功能特性
- 自动检测并锁定第一个发现的 iBeacon
- 支持指定 UUID/Major/Minor 过滤特定 beacon
- 显示 RSSI、TxPower、距离和距离分类
- 距离平滑算法（移动平均）
- 显示距离变化趋势
- 支持单次扫描和持续扫描模式

### 使用方法

#### 扫描第一个检测到的 iBeacon（单次）
```bash
python single_beacon_distance.py
```

#### 持续监控第一个检测到的 iBeacon
```bash
python single_beacon_distance.py --continuous
```

#### 指定目标 iBeacon 的 UUID
```bash
python single_beacon_distance.py --uuid FDA50693-A4E2-4FB1-AFCF-C6EB07647825 --continuous
```

#### 指定完整的 beacon 标识（UUID + Major + Minor）
```bash
python single_beacon_distance.py \
  --uuid FDA50693-A4E2-4FB1-AFCF-C6EB07647825 \
  --major 10011 \
  --minor 10925 \
  --continuous
```

#### 调整环境衰减因子（适应不同环境）
```bash
# 室内环境（建议 3.0-3.5）
python single_beacon_distance.py --env-factor 3.2 --continuous

# 开放空间（建议 2.0-2.5）
python single_beacon_distance.py --env-factor 2.3 --continuous
```

#### 调整扫描间隔
```bash
# 每 0.5 秒扫描一次（更快响应）
python single_beacon_distance.py --duration 0.5 --continuous

# 每 5 秒扫描一次（省电模式）
python single_beacon_distance.py --duration 5.0 --continuous
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--uuid` | 目标 iBeacon UUID | None (自动检测) |
| `--major` | 目标 iBeacon Major 值 | None |
| `--minor` | 目标 iBeacon Minor 值 | None |
| `--env-factor` | 环境衰减因子 | 3.0 |
| `--duration` | 每次扫描持续时间（秒） | 2.0 |
| `--continuous` | 启用持续扫描模式 | False |

### 输出示例

```
======================================================================
单个 iBeacon 距离测量程序
======================================================================
模式: 扫描第一个检测到的 iBeacon
环境衰减因子: 3.0
按 Ctrl+C 停止扫描
======================================================================

✓ 锁定目标 iBeacon:
  UUID: FDA50693-A4E2-4FB1-AFCF-C6EB07647825
  Major: 10011
  Minor: 10925

[扫描 #1] 14:32:15
----------------------------------------------------------------------
📡 RSSI: -65 dBm
📶 TxPower: -59 dBm
📏 原始距离: 2.34 米
📏 平滑距离: 2.34 米
📍 距离分类: 中距离 (Medium)

[扫描 #2] 14:32:17
----------------------------------------------------------------------
📡 RSSI: -58 dBm
📶 TxPower: -59 dBm
📏 原始距离: 1.12 米
📏 平滑距离: 1.73 米
📍 距离分类: 近距离 (Near)
📉 靠近 (变化: 0.61m)
```

### 距离分类说明

| 距离范围 | 分类 | 说明 |
|----------|------|------|
| < 0.5m | 紧邻 (Immediate) | 非常接近 |
| 0.5-2m | 近距离 (Near) | 附近 |
| 2-5m | 中距离 (Medium) | 中等距离 |
| 5-10m | 远距离 (Far) | 较远 |
| > 10m | 很远 (Very Far) | 很远 |

---

## 2. 实时距离监控工具

### 功能特性
- 实时图表显示距离变化
- 同时显示 RSSI 信号强度趋势
- 距离区间标记线（紧邻/近距离/中距离）
- 实时数据更新
- 历史数据保存（默认 50 个数据点）

### 使用方法

#### 基本使用（自动检测第一个 iBeacon）
```bash
python realtime_distance_monitor.py
```

#### 指定目标 beacon
```bash
python realtime_distance_monitor.py \
  --uuid FDA50693-A4E2-4FB1-AFCF-C6EB07647825 \
  --major 10011 \
  --minor 10925
```

#### 调整扫描间隔（更快的数据更新）
```bash
python realtime_distance_monitor.py --interval 0.5
```

#### 禁用图表（仅命令行输出）
```bash
python realtime_distance_monitor.py --no-plot
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--uuid` | 目标 UUID | None (自动检测) |
| `--major` | 目标 Major | None |
| `--minor` | 目标 Minor | None |
| `--env-factor` | 环境衰减因子 | 3.0 |
| `--interval` | 扫描间隔（秒） | 1.0 |
| `--no-plot` | 禁用图表显示 | False |

### 输出示例

图表包含两个子图：
1. **上方**: 实时距离曲线，显示当前距离和变化趋势
2. **下方**: RSSI 信号强度曲线，显示信号变化

命令行输出：
```
======================================================================
实时 iBeacon 距离监控
======================================================================
扫描间隔: 1.0 秒
环境衰减因子: 3.0
按 Ctrl+C 停止监控
======================================================================

✓ 锁定目标 iBeacon:
  UUID: FDA50693-A4E2-4FB1-AFCF-C6EB07647825
  Major: 10011
  Minor: 10925
  TxPower: -59 dBm

[14:35:21] 距离: 2.45m | RSSI: -66 dBm
[14:35:22] 距离: 2.38m | RSSI: -65 dBm
[14:35:23] 距离: 1.87m | RSSI: -62 dBm
[14:35:24] 距离: 1.56m | RSSI: -60 dBm
```

---

## 距离计算原理

### 基础公式
使用路径损耗模型：
```
distance = 10 ^ ((TxPower - RSSI) / (10 * n))
```

其中：
- `RSSI`: 接收信号强度指示（dBm）
- `TxPower`: 1米处的参考信号强度（dBm）
- `n`: 环境衰减因子

### 分段校准
为了提高不同距离范围的精度，应用了分段校准：
- **< 0.5m**: 系数 0.9（极近距离校准）
- **0.5-1m**: 系数 0.95（近距离校准）
- **> 10m**: 系数 1.1（远距离衰减补偿）

### 环境衰减因子建议值

| 环境类型 | 建议 n 值 | 说明 |
|----------|-----------|------|
| 开放空间 | 2.0 - 2.5 | 空旷室外环境 |
| 办公室 | 2.5 - 3.0 | 标准办公环境 |
| 室内复杂环境 | 3.0 - 3.5 | 有墙壁、家具的室内 |
| 密集环境 | 3.5 - 4.0 | 人群密集、障碍物多 |

---

## 提高测量精度的建议

### 1. 校准环境因子
在已知距离处测试，调整 `--env-factor` 直到距离准确：
```bash
# 在距离 beacon 2 米处测试
python single_beacon_distance.py --env-factor 3.0
# 如果显示 2.5m，尝试增加因子到 3.2
python single_beacon_distance.py --env-factor 3.2
```

### 2. 保持 beacon 稳定
- beacon 应固定放置，不要移动
- 避免用手握持 beacon（身体会吸收信号）
- 放置在稳定的平面上

### 3. 减少干扰
- 避免金属物体遮挡
- 远离其他蓝牙设备
- 避免 Wi-Fi 路由器附近

### 4. 使用平滑算法
基础工具自带移动平均，实时监控工具可以看到平滑效果。

### 5. 多次测量
在同一位置进行多次测量，取平均值。

---

## 故障排除

### 问题：未检测到 iBeacon
**解决方案：**
1. 确认 beacon 已开启且有电
2. 确认蓝牙已启用
3. 减小扫描间隔：`--duration 5.0`
4. 检查 UUID/Major/Minor 是否正确

### 问题：距离不准确
**解决方案：**
1. 调整环境衰减因子 `--env-factor`
2. 确保 beacon 的 TxPower 设置正确
3. 移除金属遮挡物
4. 使用持续模式观察距离稳定性

### 问题：距离跳动严重
**解决方案：**
1. 增加扫描间隔以获得更稳定的读数
2. 使用实时监控工具查看趋势
3. 移除环境中的干扰源

### 问题：图表无法显示（realtime_distance_monitor.py）
**解决方案：**
1. 确认已安装 matplotlib：`pip install matplotlib`
2. 如果是远程终端，使用 `--no-plot` 禁用图表

---

## 完整示例

### 场景 1: 快速测试 beacon 距离
```bash
python single_beacon_distance.py
```
等待几秒即可看到距离。

### 场景 2: 长期监控特定 beacon
```bash
python realtime_distance_monitor.py \
  --uuid FDA50693-A4E2-4FB1-AFCF-C6EB07647825 \
  --major 10011 \
  --minor 10925 \
  --interval 0.5
```
打开图表，实时观察距离和 RSSI 变化。

### 场景 3: 校准环境因子
```bash
# 站在距离 beacon 准确 3 米的位置
python single_beacon_distance.py --continuous

# 如果显示 3.5m，增加因子
python single_beacon_distance.py --env-factor 3.3 --continuous

# 如果显示 2.5m，减小因子
python single_beacon_distance.py --env-factor 2.8 --continuous

# 重复调整直到准确
```

---

## 技术支持

如有问题，请检查：
1. Python 版本 >= 3.7
2. 依赖包已安装：`pip install bleak matplotlib numpy`
3. 蓝牙已启用
4. 有足够的蓝牙权限（macOS 可能需要授权）

祝使用愉快！
