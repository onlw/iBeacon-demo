# 快速入门指南

## 第一步：安装依赖

```bash
cd /Users/hope/code/demo/iBeacon
pip install -r requirements.txt
```

## 第二步：测试解析器

运行测试脚本验证 iBeacon 数据解析功能：

```bash
python test_parser.py
```

预期输出：
```
============================================================
iBeacon 数据解析器测试
============================================================
✓ 解析成功!
  UUID: FDA50693-A4E2-4FB1-AFCF-C6EB07647825
  Major: 1
  Minor: 2
  TxPower: -59dBm
  RSSI: -65dBm
```

## 第三步：测试距离估算

运行距离估算测试：

```bash
python test_distance.py
```

这会生成一个 RSSI-距离关系曲线图。

## 第四步：配置 Beacon

编辑 `beacon_config.json`，填入你的 Beacon 参数：

1. **获取 Beacon 信息**：
   - 使用手机 App（如 "Locate Beacon" 或 "nRF Connect"）扫描 Beacon
   - 记录每个 Beacon 的 UUID、Major、Minor

2. **测量 Beacon 位置**：
   - 在房间中选择一个原点（如左下角）
   - 测量每个 Beacon 相对原点的坐标 (x, y, z)
   - 建议使用激光测距仪或卷尺

3. **更新配置文件**：
   ```json
   {
     "uuid": "你的-UUID-这里",
     "major": 1,
     "minor": 1,
     "position": [x, y, z],
     "name": "Beacon-1"
   }
   ```

## 第五步：运行系统

```bash
python main.py
```

系统会：
1. 开始扫描附近的 iBeacon
2. 计算你的 3D 位置
3. 在 3D 窗口中实时显示

## 第六步：调试优化

如果定位不准确：

1. **调整环境因子**：
   - 在配置文件中修改 `environment_factor`
   - 开阔空间：2.0 - 2.5
   - 室内一般：2.5 - 3.0
   - 复杂环境：3.0 - 3.5

2. **验证 Beacon 位置**：
   - 重新测量 Beacon 坐标
   - 确保单位统一（米）

3. **检查 Beacon 数量**：
   - 至少需要 3 个 Beacon
   - 推荐 4 个或更多

## 常见问题

### Q: 未检测到 Beacon？

A:
- 检查蓝牙是否开启
- 确认 Beacon 电量充足（LED 闪烁）
- 验证 UUID/Major/Minor 是否正确
- macOS: 在"系统偏好设置 -> 安全性与隐私 -> 蓝牙"中授权 Python

### Q: 定位误差很大？

A:
- 增加 Beacon 数量
- 调整环境衰减因子
- 避免金属物体干扰
- 确保 Beacon 位置配置准确

### Q: 可视化窗口卡顿？

A:
- 增大 `scan_interval`（如 2.0 秒）
- 减少 `max_history`（在 visualizer_3d.py 中）

## 示例配置

### 小房间（5m x 5m）

```json
{
  "beacons": [
    {"uuid": "...", "major": 1, "minor": 1, "position": [0, 0, 2.5], "name": "角落1"},
    {"uuid": "...", "major": 1, "minor": 2, "position": [5, 0, 2.5], "name": "角落2"},
    {"uuid": "...", "major": 1, "minor": 3, "position": [5, 5, 2.5], "name": "角落3"},
    {"uuid": "...", "major": 1, "minor": 4, "position": [0, 5, 2.5], "name": "角落4"}
  ],
  "environment_factor": 2.5,
  "scan_interval": 1.0,
  "room_size": [5, 5, 3]
}
```

### 办公室（10m x 8m）

```json
{
  "beacons": [
    {"uuid": "...", "major": 1, "minor": 1, "position": [1, 1, 2.5], "name": "入口"},
    {"uuid": "...", "major": 1, "minor": 2, "position": [9, 1, 2.5], "name": "窗边"},
    {"uuid": "...", "major": 1, "minor": 3, "position": [9, 7, 2.5], "name": "会议室"},
    {"uuid": "...", "major": 1, "minor": 4, "position": [1, 7, 2.5], "name": "休息区"},
    {"uuid": "...", "major": 1, "minor": 5, "position": [5, 4, 2.5], "name": "中央"}
  ],
  "environment_factor": 2.8,
  "scan_interval": 1.5,
  "room_size": [10, 8, 3]
}
```

## 下一步

- 记录轨迹到文件
- 添加楼层切换功能
- 集成室内地图
- 开发 Web 界面

祝使用愉快！
