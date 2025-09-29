from trajectory_container_tools.dataclasses import NavMsgsOdometry

# ROS Bag To TCT  Usage Guide

This guide covers how to extract trajectory data from ROS bag files using Trajectory Container Tools (TCT).

## 📚 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Basic Usage](#basic-usage)
- [Supported Message Types](#supported-message-types)
- [Advanced Examples](#advanced-examples)
- [Custom Message Types](#custom-message-types)
- [Troubleshooting](#troubleshooting)

## Overview

The ROS bag converter extracts trajectory data from ROS 2 bag files and converts them into type-safe trajectory containers. This is ideal for:
- Processing recorded robot trajectories from experiments
- Converting ROS data for analysis and visualization
- Integrating ROS workflows with trajectory analysis pipelines

## Prerequisites

### ROS Bag Requirements

- ROS2 distro and `rosbags` packages
    ```bash
    pip install rosbags
    ```
- **ROS 2 bag files** (`.db3` format with `metadata.yaml`)
- Trajectory-related topics (odometry, pose, twist messages)
- Consistent message timestamps


### Supported ROS Distributions

- ROS 2 Galactic, Humble, Iron, Jazzy
- Automatic distribution detection
- Custom typestore support

## Basic Usage

### 1. Import Required Modules

```python
from pathlib import Path
import trajectory_container_tools as tct
from trajectory_container_tools.dataclasses import NavMsgsOdometry, RosStampedDataclass
# Note: There are a lot more dataclasses available
```

### 2. Inspect ROS Bag Contents

```python
# Inspect available topics in the bag
rosbag_path = Path("path/to/your/rosbag")
tct.check_bag_topics(rosbag_path)
```

**Example Output:**
```
Available topics in rosbag:
  /odom (nav_msgs/msg/Odometry): 1245 messages
  /cmd_vel (geometry_msgs/msg/Twist): 892 messages
  /pose (geometry_msgs/msg/PoseStamped): 1245 messages
  /imu (sensor_msgs/msg/Imu): 6225 messages
```

### 3. Define Feature Configuration

```python
# Define which topics to extract and their types
features_config = {
    '/odometry': NavMsgsOdometry,     # nav_msgs/Odometry
    '/commands': ('CustomCommands', 'steering_angle', 'steering_angle_velocity', 'speed' ) 
}
```

### 4. Extract Trajectory Data

```python
# Extract multiple features from rosbag
trajectory_container = tct.from_rosbag(
    rosbag_path=rosbag_path,
    dataset_info="Robot experiment - Outdoor navigation",
    features_config=features_config
)

print(trajectory_container)
```

## Supported Message Types

### Built-in Message Types

```python
from trajectory_container_tools.dataclasses import *

# nav_msgs/Odometry -> pose + pose covariance + twist + twist covariance data
features_config = {
        '/odometry': NavMsgsOdometry
        }
```

### Dynamicaly Created Custom Messages Types

```python
features_config = {
    '/robot_pose': ('PoseCustom', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw')
}
```

## Advanced Examples

### Example 1: Multi-Topic Robot Data

```python
import trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass
from pathlib import Path
import trajectory_container_tools as tct

rosbag_path = Path("experiments/robot_nav_2024_01_15.db3").parent

# Configure multiple ROS topics
features_config = {
        # Navigation data
        '/odometry':          trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass.NavMsgsOdometry,
        '/ground_truth_pose': ('GroundTruth', 'pose_pose_position_x', 'pose_pose_position_y',
                               'pose_pose_orientation_z'),

        # Control data  
        '/velocity_commands': ('VelCmd', 'linear_x', 'linear_y', 'angular_z'),

        # Sensor data
        '/imu_readings':      ('IMUData', 'linear_acceleration_x', 'linear_acceleration_y', 'angular_velocity_z'),
        '/lidar_features':    ('LidarFeatures', 'ranges[0]', 'ranges[90]', 'ranges[180]', 'ranges[270]')
        }

# Extract trajectory data
robot_data = tct.from_rosbag(
        rosbag_path=rosbag_path,
        dataset_info="Outdoor navigation experiment - 2024-01-15",
        features_config=features_config
        )

# Access extracted data
print(f"Odometry data shape: {robot_data.topic_odometry.x.shape}")
print(f"Velocity commands shape: {robot_data.topic_velocity_commands.linear_x.shape}")
print(f"IMU data shape: {robot_data.topic_imu_readings.linear_acceleration_x.shape}")

# Analyze trajectory
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(robot_data.topic_odometry.x, robot_data.odometry.y, 'b-', label='Odometry')
plt.plot(robot_data.topic_ground_truth_pose.x, robot_data.topic_ground_truth_pose.y, 'r--', label='Ground Truth')
plt.xlabel('X Position (m)')
plt.ylabel('Y Position (m)')
plt.legend()
plt.title('Robot Trajectory Comparison')
plt.axis('equal')
plt.show()
```

### Example 2: Single Topic Extraction

```python
import trajectory_container_tools as tct

# Extract only odometry data
tc_odom = tct.extract_rosbag_feature(
        rosbag_path=rosbag_path,
        feature_name="odom",  # ROS topic name
        data_container_type=NavMsgsOdometry
        )

print(f"Odometry timestamps: {len(tc_odom.header.timestamps)}")
print(f"Position data shape: {tc_odom.topic_odom.pose.pose.position.x.shape}")
print(f"Available dimensions: {tc_odom.get_dimension_names()}")

# Access pose data
position = tc_odom.topic_odom.pose.pose.position
orientation = topic_odom.pose.pose.orientation

# Access twist data  
linear_vel = tc_odom.topic_odom.twist.linear
angular_vel = tc_odom.topic_odom.twist.angular
```

### Example 3: Time-Sliced Extraction

```python
import trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass
import trajectory_container_tools as tct

# Extract only a portion of the rosbag
partial_data = tct.from_rosbag(
        rosbag_path=rosbag_path,
        dataset_info="Partial trajectory - middle section",
        features_config={
                '/odometry': trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass.NavMsgsOdometry
                },
        start=1000,  # Start from message index 1000
        stop=5000  # Stop at message index 5000
        )

print(f"Partial trajectory length: {partial_data.topic_odometry.trajectory_len}")
```

## Custom Message Types

### Registering Custom Messages

```python
import trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass
import trajectory_container_tools as tct
from rosbags.typesys import get_types_from_msg

# Register custom message type
custom_msg_def = """
# custom_msgs/TrajectoryPoint
float64 x
float64 y  
float64 theta
float64 velocity
uint32 timestamp
"""

typestore = tct.ros.get_rosbag_typestore_auto_distro()

typestore.register(
        get_types_from_msg(custom_msg_def, 'custom_msgs/msg/TrajectoryPoint')
        )

typestore = tct.ros.register_non_native_msgs(typestore)

tc_with_custom_type = tct.from_rosbag(
        rosbag_path=rosbag_path,
        dataset_info="Trajectory with custom type",
        features_config={
                'trajectory_points': ('TrajectoryPoint', 'x', 'y', 'theta', 'velocity')
                '/odometry':         trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass.NavMsgsOdometry
                },
        typestore=typestore
        )
```

### Custom Dataclass for Complex Messages

```python
from dataclasses import dataclass
import numpy as np
from trajectory_container_tools.dataclasses import RosStampedDataclass

@dataclass
class CustomRobotState(RosStampedDataclass):
    """Custom dataclass for complex robot state messages"""
    x: np.ndarray
    y: np.ndarray
    theta: np.ndarray
    velocity: np.ndarray
    battery_level: np.ndarray

    def post_init_feature_callback(self, feature_name: str):
        """Custom processing after feature extraction"""
        if feature_name == 'theta':
            # Wrap angles to [-pi, pi]
            theta = getattr(self, feature_name)
            wrapped_theta = np.arctan2(np.sin(theta), np.cos(theta))
            setattr(self, feature_name, wrapped_theta)

            
# Use custom dataclass
tc_with_custom_type = tct.from_rosbag(
    rosbag_path=rosbag_path,
    dataset_info="Trajectory with custom dataclass",
    features_config={
        'robot_state': CustomRobotState
        },
)
```


## Troubleshooting

### Common Issues

#### 1. Topic Not Found

```
Error: Topic '/odom' not found in rosbag
```

**Solutions:**

```python
import trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass
import trajectory_container_tools as tct

# Check available topics
tct.check_bag_topics(rosbag_path)

# Common topic name variations
common_odom_topics = ['/odom', '/odometry', '/robot/odom', '/base_link/odom']

# Try different topic names
for topic in common_odom_topics:
    try:
        container = tct.extract_rosbag_feature(rosbag_path, topic,
                                               trajectory_container_tools.dataclasses.ros_msgs.ros2_stamped_dataclass.NavMsgsOdometry)
        print(f"Success with topic: {topic}")
        break
    except:
        continue
```

#### 2. Message Type Mismatch

```
Error: Expected nav_msgs/Odometry but found geometry_msgs/PoseStamped
```

**Solutions:**
```python
# Check actual message type
from rosbags.rosbag2 import Reader

with Reader(rosbag_path) as reader:
    for topic_info in reader.topics.values():
        print(f"Topic: {topic_info.name}, Type: {topic_info.msgtype}")

# Use correct dataclass for the message type
if msg_type == "geometry_msgs/msg/PoseStamped":
    features_config = {'pose': ('PoseData', 'pose_position_x', 'pose_position_y')}
```

---

## Documentation
- [Landing page](../README.md#_trajectory-container-tools_)
- [Overview and Core concept](README.md#trajectory-container-tools-documentation)
  - ↳ **[DataFrame To TCT Usage Guide](dataframe_usage.md)** - Convert pandas DataFrames to trajectory containers
  - ↳ **[TCT Direct Instantiation Guide](direct_instantiation.md)** - Create trajectory containers directly
- Interactive Jupyter notebook examples:
    - [Direct Instanciation Usage Examples](../notebooks/direct_instanciation_usage_example.ipynb) - Direct trajectory
      container instantiation
    - [ROS Bag Usage Examples](../notebooks/rosbag_usage_example.ipynb) - Extract trajectory data from ROS bags
    - [DataFrame Usage Examples](../notebooks/dataframe_usage_example.ipynb) - Convert pandas DataFrames to trajectory
      containers

