# 快速参考卡片

## 📋 常用命令

### 蓝牙扫描工具

```bash
# 基本扫描（10秒）
python scan_bluetooth_beacons.py

# 快速扫描（3秒）
python scan_bluetooth_beacons.py -d 3

# 扫描所有设备（包括非iBeacon）
python scan_bluetooth_beacons.py --all

# 按名称过滤
python scan_bluetooth_beacons.py --prefix Beacon
python scan_bluetooth_beacons.py --prefix Apple

# 生成配置文件
python scan_bluetooth_beacons.py -c beacon_config.json

# 导出JSON
python scan_bluetooth_beacons.py -e results.json

# 组合使用
python scan_bluetooth_beacons.py -d 20 --prefix Beacon -c beacons.json
```

### 定位系统

```bash
# 运行主程序
python main.py

# 模拟测试（无需真实Beacon）
python simulate_test.py

# 测试解析器
python test_parser.py

# 测试距离估算
python test_distance.py
```

## 🔧 配置文件

### beacon_config.json 结构

```json
{
  "beacons": [
    {
      "uuid": "UUID-HERE",
      "major": 1,
      "minor": 1,
      "position": [x, y, z],  // 填入实际坐标
      "name": "Beacon-1"
    }
  ],
  "environment_factor": 2.5,      // 2.0-4.0，影响距离估算
  "scan_interval": 1.0,           // 扫描间隔（秒）
  "min_beacons_required": 3,      // 最少需要3个
  "room_size": [10, 10, 3.5]      // [宽, 深, 高]
}
```

## 📊 参数调优

### environment_factor（环境衰减因子）

| 环境 | 推荐值 | 说明 |
|-----|--------|------|
| 开阔空间 | 2.0 - 2.5 | 无遮挡 |
| 普通室内 | 2.5 - 3.0 | 家具、办公室 |
| 复杂环境 | 3.0 - 3.5 | 多障碍物 |
| 金属/混凝土 | 3.5 - 4.0 | 严重遮挡 |

### scan_interval（扫描间隔）

| 值 | 效果 | 适用场景 |
|----|------|----------|
| 0.5 秒 | 高频更新 | 演示、调试 |
| 1.0 秒 | 平衡 | 正常使用 |
| 2.0 秒 | 省资源 | 后台运行 |

## 🎯 信号强度参考

| RSSI | 信号强度 | 大约距离 |
|------|---------|---------|
| >= -50 | 极强 ████████ | < 1m |
| -50 ~ -60 | 强 ██████   | 1-2m |
| -60 ~ -70 | 中 ████     | 2-5m |
| -70 ~ -80 | 弱 ██       | 5-10m |
| < -80 | 很弱 ▌       | > 10m |

## 📁 文件说明

### 核心代码（802行）

| 文件 | 行数 | 功能 |
|-----|------|------|
| main.py | 217 | 主程序 |
| ibeacon_scanner.py | 97 | BLE扫描 |
| ibeacon_parser.py | 95 | 数据解析 |
| positioning_3d.py | 177 | 定位算法 |
| visualizer_3d.py | 216 | 3D可视化 |
| **scan_bluetooth_beacons.py** | **319** | **扫描工具** |

### 文档（5篇）

| 文件 | 内容 |
|-----|------|
| README.md | 完整使用说明 |
| QUICKSTART.md | 快速开始（6步） |
| PROJECT_OVERVIEW.md | 架构和算法 |
| API_REFERENCE.md | API文档 |
| SCAN_TOOL_GUIDE.md | 扫描工具指南 |
| SUMMARY.md | 项目总结 |

## 🚀 工作流程

### 1. 初次使用

```bash
# 安装 → 扫描 → 配置 → 运行
pip install -r requirements.txt
python scan_bluetooth_beacons.py -c beacon_config.json
# 编辑 beacon_config.json 填入位置
python main.py
```

### 2. 调试定位

```bash
# 扫描查看信号
python scan_bluetooth_beacons.py -d 20 -e signal.json

# 调整 environment_factor

# 重新运行
python main.py
```

### 3. 测试验证

```bash
# 依次运行
python test_parser.py        # 解析器
python test_distance.py      # 距离
python simulate_test.py      # 模拟
python scan_bluetooth_beacons.py  # 扫描
python main.py               # 定位
```

## 🔍 故障排除

### 未发现设备
- ✓ 检查蓝牙是否开启
- ✓ 确认 Beacon 电量充足
- ✓ 检查系统蓝牙权限（macOS）
- ✓ 靠近 Beacon 设备

### 定位不准确
- ✓ 调整 environment_factor（±0.5）
- ✓ 增加 Beacon 数量（4+个）
- ✓ 重新测量 Beacon 位置
- ✓ 避免金属物体干扰

### 可视化问题
- ✓ 检查 matplotlib 安装
- ✓ 尝试更换后端（TkAgg/Qt5Agg）

## 📞 获取帮助

```bash
# 查看帮助
python scan_bluetooth_beacons.py --help
python main.py --help

# 查看文档
cat README.md
cat QUICKSTART.md
cat SCAN_TOOL_GUIDE.md
```

## 💡 小技巧

1. **快速查看周围Beacon**: `python scan_bluetooth_beacons.py -d 3`
2. **信号测试**: `python scan_bluetooth_beacons.py -d 20 -e test.json`
3. **模拟演示**: `python simulate_test.py`
4. **调整精度**: 修改 `environment_factor`
5. **批量扫描**: `watch -n 15 python scan_bluetooth_beacons.py -d 5`

---

**保存此卡片以便快速查阅！**
