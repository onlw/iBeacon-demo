"""
测试 RSSI 距离估算功能
"""
from ibeacon_scanner import DistanceEstimator
import numpy as np
import matplotlib.pyplot as plt


def test_distance_estimation():
    """测试距离估算"""
    print("=" * 60)
    print("RSSI 距离估算测试")
    print("=" * 60)

    estimator = DistanceEstimator()
    tx_power = -59  # 1米处的信号强度

    # 测试不同 RSSI 值
    test_cases = [
        (-59, "1米"),
        (-65, "~2米"),
        (-70, "~3-4米"),
        (-75, "~5-7米"),
        (-80, "~10米"),
        (-85, "~15米"),
    ]

    print(f"TxPower: {tx_power}dBm")
    print(f"环境衰减因子 n: 2.5 (室内标准)")
    print()

    results = []
    for rssi, expected in test_cases:
        distance = estimator.estimate_distance(rssi, tx_power, n=2.5)
        results.append((rssi, distance))
        print(f"RSSI: {rssi:3d}dBm -> 估算距离: {distance:6.2f}m (预期: {expected})")

    print()
    print("=" * 60)

    # 绘制 RSSI vs 距离曲线
    rssi_range = np.arange(-50, -90, -1)
    distances = [estimator.estimate_distance(r, tx_power, n=2.5) for r in rssi_range]

    plt.figure(figsize=(10, 6))
    plt.plot(rssi_range, distances, 'b-', linewidth=2, label='n=2.5 (室内)')

    # 不同环境因子
    for n, label in [(2.0, '理想环境'), (3.0, '复杂环境'), (3.5, '严重遮挡')]:
        distances_n = [estimator.estimate_distance(r, tx_power, n=n) for r in rssi_range]
        plt.plot(rssi_range, distances_n, '--', alpha=0.6, label=f'n={n} ({label})')

    plt.xlabel('RSSI (dBm)', fontsize=12)
    plt.ylabel('距离 (米)', fontsize=12)
    plt.title('RSSI 与距离关系曲线', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xlim(-90, -50)
    plt.ylim(0, 30)

    # 标注测试点
    for rssi, distance in results:
        plt.plot(rssi, distance, 'ro', markersize=8)

    plt.tight_layout()
    plt.savefig('rssi_distance_curve.png', dpi=150)
    print("✓ RSSI-距离曲线已保存为: rssi_distance_curve.png")
    plt.show()


if __name__ == '__main__':
    test_distance_estimation()
