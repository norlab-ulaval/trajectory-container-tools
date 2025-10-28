# coding=utf-8

"""
Integration test based on `notebooks/rosbag_usage_example.ipynb`
section 5 "Advanced Processing with Custom Post-Processing Callback"
"""

import trajectory_container_tools as tct
from dataclasses import dataclass
import os
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class RacingOdometryAnalysis(tct.dataclasses.NavMsgsOdometry):
    """Custom odometry analysis for racing applications."""

    def post_init_feature_callback(self, feature_name):
        """Calculate racing-specific metrics."""

        if feature_name == "pose":
            # Calculate trajectory metrics when position data is processed
            x = self.get_dynamic_attribute("pose.pose.position.x")
            y = self.get_dynamic_attribute("pose.pose.position.y")

            # Calculate path length
            dx = np.diff(x)
            dy = np.diff(y)
            segment_lengths = np.sqrt(dx ** 2 + dy ** 2)
            path_length = np.sum(segment_lengths)
            self.set_dynamic_attribute('path_length', path_length)

        elif feature_name == "twist":
            # Calculate acceleration when velocity data is processed
            _vel_x = self.get_dynamic_attribute("twist.twist.linear.x")
            _vel_y = self.get_dynamic_attribute("twist.twist.linear.y")

            # Calculate speed and acceleration
            _speed = np.sqrt(_vel_x ** 2 + _vel_y ** 2)
            self.set_dynamic_attribute('speed', _speed)

            if len(self.header.timestamps) > 1:
                dt = self.header.timestamps.delta_stamps
                acceleration = np.diff(_speed) / dt[1:]
                # Pad to match length
                self.set_dynamic_attribute('acceleration', np.concatenate([[0], acceleration]))
            else:
                self.set_dynamic_attribute('acceleration', np.zeros_like(_speed))

        return None


def plot_racing_analysis(racing_data, title: str = "Racing Performance Analysis"):
    """Plot comprehensive racing analysis."""
    odom = racing_data.topic_odom

    fig = plt.figure(figsize=(15, 6))

    # Create a 2x3 grid of subplots
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1])

    # 1. Trajectory with speed colormap
    ax1 = fig.add_subplot(gs[:, 0])
    x = odom.pose.pose.position.x
    y = odom.pose.pose.position.y

    scatter = ax1.scatter(x, y, c=odom.speed, cmap='viridis', s=20, alpha=0.8)
    ax1.plot(x, y, 'k-', alpha=0.3, linewidth=1)
    ax1.scatter(x[0], y[0], color='green', s=200, marker='o',
                label='Start', edgecolor='black', linewidth=3, zorder=5)
    ax1.scatter(x[-1], y[-1], color='red', s=200, marker='s',
                label='End', edgecolor='black', linewidth=3, zorder=5)

    cbar = plt.colorbar(scatter, )
    cbar.set_label('Speed (m/s)', fontsize=12)
    ax1.set_xlabel('X Position (m)')
    ax1.set_ylabel('Y Position (m)')
    ax1.set_title(f'{title} - Speed Profile on Track')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')

    # 2. Speed vs time
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(odom.timesteps_indices, odom.speed, 'b-', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Speed (m/s)')
    ax2.set_title('Speed vs Time')
    ax2.grid(True, alpha=0.3)

    # 3. Acceleration vs time
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(odom.timesteps_indices, odom.acceleration, 'r-', linewidth=2)
    ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Acceleration (m/s²)')
    ax3.set_title('Acceleration vs Time')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

def test_integration_rosbag_usage_example():
    BAG = "2024-03-21_14-52-35-filtered"
    rosbag_path = os.path.join("data", "repository_data", "tests_data", "rosbag_test_data",
                               "rosbag-vaul-f110-grand-salon-raw-msg", BAG)
    rosbag_path = tct.extractor.show_rosbag_summary_info(rosbag_path)

    print(f"Using ROS bag: {rosbag_path}")

    multi_features_config = {
            "/odom":            RacingOdometryAnalysis,
            "/sensors/imu/raw": tct.dataclasses.SensorMsgsImu,
            "/teleop":          tct.dataclasses.AckermannMsgsAckermannDriveStamped,
            }

    multi_data = tct.extractor.from_rosbag(rosbag_path, dataset_info="Multi-sensor F110 data analysis",
                                           features_config=multi_features_config, start=None,
                                           stop=None,
                                           chunk_on="/teleop")

    print(multi_data)

    print(f"\nRacing Analysis Results:")
    print(f"  Total path length: {multi_data.topic_odom.path_length} meters")
    print(f"  Maximum speed: {np.max(multi_data.topic_odom.speed):.2f} m/s")
    print(f"  Maximum acceleration: {np.max(np.abs(multi_data.topic_odom.acceleration)):.2f} m/s²")

    # Create racing analysis visualization
    plot_racing_analysis(multi_data, multi_data.dataset_info)
    # plt.show()
