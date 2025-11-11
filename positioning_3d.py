"""
3D 定位算法模块
使用三边测量（Trilateration）和优化方法计算 3D 位置
"""
import numpy as np
from scipy.optimize import minimize
from typing import List, Tuple, Optional


class Position3D:
    """3D 位置计算器"""

    @staticmethod
    def trilateration_3d(beacons: List[Tuple[np.ndarray, float]]) -> Optional[np.ndarray]:
        """
        使用三边测量计算 3D 位置

        Args:
            beacons: [(position, distance), ...] 列表
                    position 是 numpy 数组 [x, y, z]
                    distance 是到该 beacon 的距离

        Returns:
            估算的 3D 位置 [x, y, z]，如果无法计算则返回 None
        """
        if len(beacons) < 3:
            return None

        # 使用最小二乘法优化
        return Position3D.least_squares_3d(beacons)

    @staticmethod
    def least_squares_3d(beacons: List[Tuple[np.ndarray, float]],
                        initial_guess: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        使用最小二乘法优化计算 3D 位置

        Args:
            beacons: [(position, distance), ...] 列表
            initial_guess: 初始猜测位置，如果为 None 则使用加权平均位置

        Returns:
            优化后的 3D 位置 [x, y, z]
        """
        if len(beacons) < 3:
            return None

        # 如果没有提供初始猜测，使用加权平均作为更好的初始值
        if initial_guess is None:
            initial_guess = Position3D.weighted_position(beacons)
            if initial_guess is None:
                positions = np.array([b[0] for b in beacons])
                initial_guess = np.mean(positions, axis=0)

        def error_function(pos):
            """
            加权误差函数：距离越近的 beacon 权重越大
            """
            error = 0.0
            for beacon_pos, measured_distance in beacons:
                # 计算欧几里得距离
                calculated_distance = np.linalg.norm(pos - beacon_pos)
                # 距离倒数作为权重（距离越近越重要）
                weight = 1.0 / (measured_distance + 0.5)
                # 累加加权误差平方
                error += weight * (calculated_distance - measured_distance) ** 2
            return error

        # 使用 scipy.optimize.minimize 进行优化
        result = minimize(
            error_function,
            initial_guess,
            method='Nelder-Mead',
            options={'maxiter': 1000, 'xatol': 1e-8, 'fatol': 1e-8}
        )

        if result.success:
            return result.x
        else:
            # 即使优化不完全成功，也返回最佳结果
            return result.x

    @staticmethod
    def filter_outliers(beacons: List[Tuple[np.ndarray, float]],
                       max_distance: float = 50.0) -> List[Tuple[np.ndarray, float]]:
        """
        过滤异常距离值

        Args:
            beacons: beacon 列表
            max_distance: 最大合理距离（米）

        Returns:
            过滤后的 beacon 列表
        """
        return [(pos, dist) for pos, dist in beacons if 0 < dist < max_distance]

    @staticmethod
    def weighted_position(beacons: List[Tuple[np.ndarray, float]]) -> Optional[np.ndarray]:
        """
        使用加权平均计算位置（距离越近权重越大）

        Args:
            beacons: [(position, distance), ...] 列表

        Returns:
            加权平均位置 [x, y, z]
        """
        if not beacons:
            return None

        # 使用距离倒数作为权重（距离越近权重越大）
        weights = np.array([1.0 / (d + 0.1) for _, d in beacons])  # 加 0.1 避免除零
        weights /= np.sum(weights)  # 归一化

        # 计算加权平均位置
        weighted_pos = np.zeros(3)
        for i, (pos, _) in enumerate(beacons):
            weighted_pos += weights[i] * pos

        return weighted_pos


class KalmanFilter3D:
    """简单的 3D 卡尔曼滤波器，用于平滑位置估算"""

    def __init__(self, process_variance: float = 1e-3, measurement_variance: float = 0.1):
        """
        初始化卡尔曼滤波器

        Args:
            process_variance: 过程噪声方差
            measurement_variance: 测量噪声方差
        """
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_position = None
        self.estimation_error = np.eye(3)

    def update(self, measured_position: np.ndarray) -> np.ndarray:
        """
        更新滤波器

        Args:
            measured_position: 测量得到的位置

        Returns:
            滤波后的位置
        """
        if self.estimated_position is None:
            # 第一次测量，直接使用测量值
            self.estimated_position = measured_position.copy()
            return self.estimated_position

        # 预测步骤
        predicted_position = self.estimated_position
        predicted_error = self.estimation_error + self.process_variance * np.eye(3)

        # 更新步骤
        measurement_cov = self.measurement_variance * np.eye(3)
        kalman_gain = predicted_error @ np.linalg.inv(predicted_error + measurement_cov)
        self.estimated_position = predicted_position + kalman_gain @ (measured_position - predicted_position)
        self.estimation_error = (np.eye(3) - kalman_gain) @ predicted_error

        return self.estimated_position
