# 蓝牙信标扫描工具使用指南

## 功能特性

- ✅ 扫描附近所有蓝牙设备
- ✅ 自动识别 iBeacon 设备
- ✅ 支持设备名称前缀过滤
- ✅ 显示信号强度（RSSI）和信号条
- ✅ 导出扫描结果为 JSON
- ✅ 自动生成 beacon_config.json 配置文件
- ✅ 按信号强度排序显示

## 快速开始

### 基本用法

```bash
# 扫描所有 iBeacon（默认 10 秒）
python scan_bluetooth_beacons.py
```

### 扫描所有蓝牙设备

```bash
# 显示所有蓝牙设备（包括非 iBeacon）
python scan_bluetooth_beacons.py --all
```

### 按名称前缀过滤

```bash
# 只显示名称以 "Beacon" 开头的设备
python scan_bluetooth_beacons.py --prefix Beacon

# 只显示名称以 "Apple" 开头的设备
python scan_bluetooth_beacons.py --prefix Apple

# 只显示名称以 "iBeacon" 开头的设备
python scan_bluetooth_beacons.py --prefix iBeacon
```

### 自定义扫描时长

```bash
# 扫描 20 秒
python scan_bluetooth_beacons.py --duration 20

# 扫描 5 秒（快速扫描）
python scan_bluetooth_beacons.py -d 5
```

### 组合使用

```bash
# 扫描 30 秒，显示所有以 "Beacon" 开头的设备（包括非 iBeacon）
python scan_bluetooth_beacons.py --prefix Beacon --duration 30 --all
```

## 导出功能

### 导出为 JSON

```bash
# 导出扫描结果为 JSON 文件
python scan_bluetooth_beacons.py --export results.json

# 扫描 20 秒并导出
python scan_bluetooth_beacons.py -d 20 -e scan_results.json
```

**导出的 JSON 格式:**
```json
{
  "scan_time": "2025-11-11T19:30:00",
  "total_devices": 3,
  "devices": [
    {
      "address": "AA:BB:CC:DD:EE:FF",
      "name": "Beacon-1",
      "rssi": -65,
      "is_ibeacon": true,
      "ibeacon": {
        "uuid": "FDA50693-A4E2-4FB1-AFCF-C6EB07647825",
        "major": 1,
        "minor": 1,
        "tx_power": -59
      }
    }
  ]
}
```

### 生成 beacon_config.json

```bash
# 自动生成定位系统配置文件
python scan_bluetooth_beacons.py --config my_beacons.json

# 扫描并同时导出两种格式
python scan_bluetooth_beacons.py -e results.json -c beacon_config.json
```

生成的配置文件可以直接用于 `main.py` 定位系统，但需要手动填入每个 Beacon 的实际 3D 位置坐标。

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|-----|------|------|--------|
| `--prefix` | `-p` | 设备名称前缀过滤 | 无（显示所有） |
| `--duration` | `-d` | 扫描持续时间（秒） | 10.0 |
| `--all` | `-a` | 显示所有蓝牙设备 | False（仅 iBeacon） |
| `--export` | `-e` | 导出为 JSON 文件 | 无 |
| `--config` | `-c` | 导出为 beacon_config.json | 无 |
| `--help` | `-h` | 显示帮助信息 | - |

## 输出示例

### iBeacon 设备输出

```
================================================================================
🔍 蓝牙信标扫描工具
================================================================================
扫描时长: 10.0 秒
模式: 仅显示 iBeacon 设备
开始时间: 2025-11-11 19:30:00
================================================================================

⏳ 正在扫描...

✓ 扫描完成！共发现 3 个设备

================================================================================
📱 扫描结果
================================================================================

🔶 iBeacon 设备 (3 个)
--------------------------------------------------------------------------------
1. Beacon-1
   地址: AA:BB:CC:DD:EE:FF
   UUID: FDA50693-A4E2-4FB1-AFCF-C6EB07647825
   Major: 1
   Minor: 1
   TxPower: -59 dBm
   RSSI: -65 dBm  ██████   (强)
   最后更新: 19:30:05

2. Beacon-2
   地址: 11:22:33:44:55:66
   UUID: FDA50693-A4E2-4FB1-AFCF-C6EB07647825
   Major: 1
   Minor: 2
   TxPower: -59 dBm
   RSSI: -72 dBm  ████     (中)
   最后更新: 19:30:08
```

### 所有设备输出（--all 模式）

```
🔶 iBeacon 设备 (2 个)
--------------------------------------------------------------------------------
[iBeacon 设备信息...]

📡 其他蓝牙设备 (5 个)
--------------------------------------------------------------------------------
1. iPhone
   地址: AA:BB:CC:DD:EE:FF
   RSSI: -45 dBm  ████████ (极强)
   最后更新: 19:30:10

2. MacBook Pro
   地址: 11:22:33:44:55:66
   RSSI: -68 dBm  ████     (中)
   最后更新: 19:30:12
```

## 信号强度说明

| RSSI 范围 | 信号条 | 强度 | 大约距离 |
|----------|--------|------|---------|
| >= -50 dBm | ████████ | 极强 | < 1m |
| -50 ~ -60 dBm | ██████   | 强 | 1-2m |
| -60 ~ -70 dBm | ████     | 中 | 2-5m |
| -70 ~ -80 dBm | ██       | 弱 | 5-10m |
| < -80 dBm | ▌        | 很弱 | > 10m |

## 使用场景

### 1. 发现附近的 iBeacon

```bash
# 快速扫描附近的 iBeacon
python scan_bluetooth_beacons.py -d 5
```

### 2. 调试 Beacon 部署

```bash
# 扫描 30 秒，查看所有 Beacon 的信号强度
python scan_bluetooth_beacons.py --duration 30 --export beacon_signal.json
```

### 3. 生成定位系统配置

```bash
# 扫描并生成配置文件
python scan_bluetooth_beacons.py -d 15 -c beacon_config.json

# 然后手动编辑 beacon_config.json，填入每个 Beacon 的位置
# 最后运行定位系统
python main.py
```

### 4. 查找特定 Beacon

```bash
# 只查找名称以 "MyBeacon" 开头的设备
python scan_bluetooth_beacons.py --prefix MyBeacon
```

### 5. 监控蓝牙环境

```bash
# 查看附近所有蓝牙设备（不仅是 iBeacon）
python scan_bluetooth_beacons.py --all --duration 20
```

## 故障排除

### 未发现任何设备

**可能原因:**
- 蓝牙未开启
- Beacon 距离过远
- Beacon 电量耗尽
- 没有蓝牙权限

**解决方法:**
1. 检查系统蓝牙是否开启
2. 靠近 Beacon 设备
3. 确认 Beacon LED 正在闪烁
4. macOS: 在"系统偏好设置 -> 安全性与隐私"中授权 Python 蓝牙权限

### 只发现部分设备

**可能原因:**
- 名称前缀过滤太严格
- 扫描时间太短
- 某些设备广播间隔较长

**解决方法:**
1. 移除 `--prefix` 参数或使用更通用的前缀
2. 增加扫描时长：`--duration 20`
3. 确保设备在广播模式

### macOS 权限问题

如果提示权限错误：

1. 打开"系统偏好设置"
2. 进入"安全性与隐私" -> "蓝牙"
3. 确保 Terminal 或 iTerm 有蓝牙权限
4. 重新运行脚本

## 高级用法

### 连续监控

使用 watch 命令持续扫描：

```bash
# 每 15 秒扫描一次
watch -n 15 python scan_bluetooth_beacons.py -d 5
```

### 批量扫描并保存历史

```bash
# 每次扫描保存带时间戳的文件
python scan_bluetooth_beacons.py -e "scan_$(date +%Y%m%d_%H%M%S).json"
```

### 结合 grep 过滤输出

```bash
# 只显示包含 "Beacon" 的行
python scan_bluetooth_beacons.py --all | grep Beacon
```

## 与定位系统集成

1. **扫描并生成配置:**
   ```bash
   python scan_bluetooth_beacons.py -d 15 -c beacon_config.json
   ```

2. **测量 Beacon 位置:**
   - 使用卷尺或激光测距仪测量每个 Beacon 的 3D 坐标

3. **编辑配置文件:**
   ```json
   {
     "beacons": [
       {
         "uuid": "...",
         "major": 1,
         "minor": 1,
         "position": [0.0, 0.0, 2.5],  // 修改为实际坐标
         "name": "Beacon-1"
       }
     ]
   }
   ```

4. **运行定位系统:**
   ```bash
   python main.py
   ```

## 常见 iBeacon UUID

一些常见的 iBeacon UUID 供参考：

- **Apple iBeacon**: `FDA50693-A4E2-4FB1-AFCF-C6EB07647825`
- **Estimote**: `B9407F30-F5F8-466E-AFF9-25556B57FE6D`
- **Kontakt.io**: `F7826DA6-4FA2-4E98-8024-BC5B71E0893E`
- **自定义**: 你可以生成自己的 UUID

## 小技巧

1. **快速查看**: 使用 `-d 3` 进行 3 秒快速扫描
2. **完整扫描**: 使用 `-d 30` 进行 30 秒完整扫描，确保不遗漏设备
3. **调试信号**: 使用 `--all` 查看所有蓝牙设备，排除干扰
4. **批量处理**: 导出 JSON 后可用 Python 或 jq 工具进一步处理

## 相关命令

```bash
# 查看帮助
python scan_bluetooth_beacons.py --help

# 测试解析器
python test_parser.py

# 运行定位系统
python main.py

# 模拟测试
python simulate_test.py
```

祝使用愉快！
