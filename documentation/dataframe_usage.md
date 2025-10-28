# DataFrame To TCT Usage Guide

This guide covers how to convert pandas DataFrames to trajectory containers using Trajectory Container Tools (TCT).

## 📚 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Basic Usage](#basic-usage)
- [Feature Configuration](#feature-configuration)
- [Advanced Examples](#advanced-examples)
- [Custom Post-Processing](#custom-post-processing)
- [Data Validation](#data-validation)
- [Troubleshooting](#troubleshooting)

## Overview

The DataFrame converter allows you to transform structured pandas DataFrames into type-safe trajectory containers. This is ideal for:
- Converting experimental datasets to standardized trajectory format
- Integrating with existing pandas-based workflows

## Prerequisites

### DataFrame Structure Requirements

Your DataFrame must have one of these structures:

**Option 1: Batch Trajectories**
- One trajectory per row
- Features with timestep indices in column names: `feature_1`, `feature_2`, ..., `feature_N`
- Each cell contains a single timestep value

**Option 2: Single Trajectory**
- One timestep per row
- Feature dimensions as separate columns
- Consistent timestep indexing

### Example DataFrame Structure

```python
import pandas as pd
import numpy as np

# Example batch trajectory DataFrame
data = {
    'trajectory_id': [0, 1, 2],
    'pose_x_1': [0.0, 1.0, 2.0],    # timestep 1
    'pose_x_2': [0.1, 1.1, 2.1],    # timestep 2  
    'pose_x_3': [0.2, 1.2, 2.2],    # timestep 3
    'pose_y_1': [0.0, 0.0, 0.0],
    'pose_y_2': [0.1, 0.1, 0.1],
    'pose_y_3': [0.2, 0.2, 0.2],
    'pose_yaw_1': [0.0, 0.1, 0.2],
    'pose_yaw_2': [0.1, 0.2, 0.3],
    'pose_yaw_3': [0.2, 0.3, 0.4]
}
df = pd.DataFrame(data)
```

## Basic Usage

### 1. Import Required Modules

```python
import trajectory_container_tools as tct

from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    StatePose2D, 
    StatePose3D, 
    Velocity, 
    VelocitySkidSteer, 
    CmdStandard, 
    CmdSkidSteer
)
```

### 2. Inspect Your DataFrame

```python
# Load and inspect your data
dataset_path = "path/to/your/data.pkl"
df, actual_path = tct.extractor.unpack_dataframe_and_show_topic(dataset_path)

print(f"DataFrame shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())
```

### 3. Define Feature Configuration

```python
# Define which features to extract and their types
features_config = {
    'pose': StatePose2D,           # Uses predefined 2D pose class
    'velocity': Velocity,          # Uses predefined velocity class
    'commands': CmdStandard        # Uses predefined command class
}
```

### 4. Convert DataFrame to Trajectory Container

```python
import trajectory_container_tools as tct

# Convert multiple features
trajectory_container = tct.extractor.from_dataframe(
    dataset_frame=df,
    dataset_info="Robot navigation experiment - Lab conditions",
    features_config=features_config
)

print(trajectory_container)
```

## Feature Configuration

### Predefined Dataclasses

TCT provides several predefined trajectory dataclasses:

#### Pose Dataclasses

```python
from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    StatePose2D,  # x, y, yaw
    StatePose3D  # x, y, z, roll, pitch, yaw  
    )

features_config = {
        'robot_pose_2d': StatePose2D,
        'robot_pose_3d': StatePose3D
        }
```

#### Velocity Dataclasses

```python
from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    Velocity,  # vx, vy, vtheta
    VelocitySkidSteer  # left_vel, right_vel
    )

features_config = {
        'body_velocity':  Velocity,
        'wheel_velocity': VelocitySkidSteer
        }
```

#### Command Dataclasses

```python
from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    CmdStandard,  # linear_x, linear_y, angular_z
    CmdSkidSteer  # left_cmd, right_cmd
    )

features_config = {
        'velocity_commands': CmdStandard,
        'motor_commands':    CmdSkidSteer
        }
```

### Custom Dataclasses with Tuples

For custom features not covered by predefined classes:

```python
features_config = {
    'custom_sensor': ('SensorData', 'sensor_1', 'sensor_2', 'sensor_3'),
    'imu_data': ('IMUReading', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z'),
    'pose_3d': ('CustomPose3D', 'x', 'y', 'z', 'roll', 'pitch', 'yaw')
}
```

## Advanced Examples

### Example 1: Multi-Feature Robotics Dataset

```python
import pandas as pd
import trajectory_container_tools as tct 
from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import *

# Load robotics dataset
df = pd.read_pickle("robot_trajectories.pkl")

# Configure multiple features
features_config = {
        'odometry':          StatePose2D,
        'ground_truth':      StatePose2D,
        'velocity_estimate': Velocity,
        'control_commands':  CmdStandard,
        'imu_raw':           ('IMUData', 'accel_x', 'accel_y', 'accel_z', 'gyro_z'),
        'lidar_features':    ('LidarFeatures', 'range_front', 'range_left', 'range_right')
        }

# Convert to trajectory container
multi_feature_container = tct.extractor.from_dataframe(
        dataset_frame=df,
        dataset_info="Multi-sensor robot navigation dataset",
        features_config=features_config
        )

# Access trajectory data
print(f"Dataset contains {multi_feature_container.odometry.trajectory_len} timesteps")
print(f"Number of trajectories: {multi_feature_container.odometry.x.shape[0]}")

# Access specific features
robot_x_positions = multi_feature_container.odometry.x
robot_velocities = multi_feature_container.velocity_estimate.vx
control_linear_x = multi_feature_container.control_commands.linear_x
```

### Example 2: Single Feature Extraction

```python
import trajectory_container_tools as tct

# Extract only pose data
pose_container = tct.extractor.extract_dataframe_feature(dataset=df, feature_name="odometry",
                                           data_container_type=StatePose2D)

print(f"Pose data shape: {pose_container.x.shape}")
print(f"Available dimensions: {pose_container.get_public_attribute_names()}")
```

## Custom Post-Processing

Create custom dataclasses with specialized processing:

### Example: Steady-State Analysis

```python
from dataclasses import dataclass
import numpy as np
import trajectory_container_tools as tct

@dataclass
class StatePose2DSteadyState(tct.dataclasses.StatePose2D):
    """Custom pose class that computes steady-state metrics"""
    
    def post_init_feature_callback(self, feature_name: str):
        """Called after feature initialization"""
        feature = getattr(self, feature_name)
        
        if isinstance(feature, np.ndarray):
            # Compute initial values for each trajectory
            if self.current_trj_axe == -1:
                # Time axis is last dimension
                initial_value = feature[..., 0]
            else:
                # Time axis is first dimension  
                initial_value = feature[0, ...]
            
            # Store initial value as new attribute
            setattr(self, f"{feature_name}_initial", initial_value)
            
            # Compute steady-state deviation
            deviation = feature - initial_value
            setattr(self, f"{feature_name}_deviation", deviation)
        
        # Call parent post-processing
        super().post_init_feature_callback(feature_name)

# Use custom class
features_config = {
    'steady_state_pose': StatePose2DSteadyState,
    'reference_pose': tct.dataclasses.StatePose2D
}

container = tct.extractor.from_dataframe(df, "Steady-state analysis", features_config)

# Access computed metrics
initial_x = container.steady_state_pose.x_initial
x_deviation = container.steady_state_pose.x_deviation
```

### Example: Data Filtering and Transformation

```python
import trajectory_container_tools as tct

@dataclass
class FilteredVelocity(tct.dataclasses.Velocity):
    """Velocity class with filtering and outlier removal"""
    
    def post_init_feature_callback(self, feature_name: str):
        feature = getattr(self, feature_name)
        
        if isinstance(feature, np.ndarray) and feature_name in ['vx', 'vy']:
            # Apply moving average filter
            from scipy.ndimage import uniform_filter1d
            
            # Filter along time axis
            axis = -1 if self.current_trj_axe == -1 else 0
            filtered_feature = uniform_filter1d(feature, size=5, axis=axis)
            
            # Remove outliers (values > 3 std)
            mean_val = np.mean(filtered_feature, axis=axis, keepdims=True)
            std_val = np.std(filtered_feature, axis=axis, keepdims=True)
            mask = np.abs(filtered_feature - mean_val) <= 3 * std_val
            filtered_feature = np.where(mask, filtered_feature, mean_val)
            
            # Update the feature
            setattr(self, feature_name, filtered_feature)
        
        super().post_init_feature_callback(feature_name)
```

## Data Validation

### Automatic Validation

TCT performs automatic validation for:
- Consistent timestep indexing
- Uniform array shapes across dimensions
- Monotonic timestamp progression

### Manual Validation

```python
import trajectory_container_tools as tct

# Validate DataFrame structure before conversion
feature_names = ['pose', 'velocity', 'commands']
try:
    tct.temporal.validate_dataframe_timesteps_indexing(df, feature_names)
    print("DataFrame structure is valid")
except Exception as e:
    print(f"Validation error: {e}")
```

### Custom Validation

```python
import trajectory_container_tools as tct

@dataclass
class ValidatedPose(tct.dataclasses.StatePose2D):
    """Pose class with custom validation"""
    
    def post_init_feature_callback(self, feature_name: str):
        feature = getattr(self, feature_name)
        
        if isinstance(feature, np.ndarray):
            # Custom validation logic
            if feature_name == 'x' and np.any(np.abs(feature) > 100):
                raise ValueError(f"X positions exceed reasonable bounds: max={np.max(np.abs(feature))}")
            
            if feature_name == 'yaw':
                # Wrap angles to [-pi, pi]
                wrapped_yaw = np.arctan2(np.sin(feature), np.cos(feature))
                setattr(self, feature_name, wrapped_yaw)
        
        super().post_init_feature_callback(feature_name)
```

## Best Practices

### 1. Data Organization

```python
from trajectory_container_tools.dataclasses import StatePose2D, Velocity, CmdStandard, CmdSkidSteer

# Organize features logically
features_config = {
    # State estimation
    'odometry': StatePose2D,
    'ground_truth': StatePose2D,
    'velocity_estimate': Velocity,
    
    # Control
    'velocity_commands': CmdStandard,
    'motor_commands': CmdSkidSteer,
    
    # Sensing
    'imu_data': ('IMUData', 'accel_x', 'accel_y', 'gyro_z'),
    'lidar_scan': ('LidarData', 'range_0', 'range_90', 'range_180', 'range_270')
}
```

### 2. Configuration Management

```python
from trajectory_container_tools.dataclasses import StatePose2D, Velocity

# Use configuration dictionaries for reproducibility
EXPERIMENT_CONFIG = {
    'dataset_info': 'Experiment 2024-01-15: Indoor navigation',
    'features_config': {
        'robot_pose': StatePose2D,
        'target_pose': StatePose2D,
        'velocity': Velocity
    }
}

def load_trajectory_data(df_path, config=EXPERIMENT_CONFIG):
    df = pd.read_pickle(df_path)
    
    return from_dataframe(
        dataset_frame=df,
        dataset_info=config['dataset_info'],
        features_config=config['features_config']
    )
```

### 3. Error Handling

```python
import trajectory_container_tools as tct

def safe_trajectory_conversion(df, features_config, dataset_info=""):
    """Safely convert DataFrame with error handling"""
    try:
        # Validate first
        feature_names = list(features_config.keys())
        tct.temporal.validate_dataframe_timesteps_indexing(df, feature_names)
        
        # Convert
        container = tct.extractor.from_dataframe(
            dataset_frame=df,
            dataset_info=dataset_info,
            features_config=features_config
        )
        
        return container, None
        
    except Exception as e:
        print(f"Conversion failed: {e}")
        return None, str(e)

# Usage
container, error = safe_trajectory_conversion(df, features_config, "Test dataset")
if container is not None:
    print("Conversion successful!")
else:
    print(f"Conversion failed: {error}")
```

## Troubleshooting

### Common Issues

#### 1. Column Name Mismatch
```
Error: KeyError: 'pose_x_1' not found
```
**Solution**: Ensure your DataFrame columns match the expected pattern:
```python
# Check your column names
print(df.columns.tolist())

# Expected pattern: feature_dimension_timestep
# e.g., pose_x_1, pose_x_2, pose_y_1, pose_y_2
```

#### 2. Inconsistent Array Shapes
```
Error: Arrays have inconsistent shapes
```
**Solution**: Ensure all timestep columns have the same number of values:
```python
# Check for missing values
print(df.isnull().sum())

# Check column consistency
pose_cols = [col for col in df.columns if 'pose_x_' in col]
print([df[col].shape for col in pose_cols])
```

#### 3. Invalid Timestep Indices
```
Error: Non-monotonic timestep indices detected
```
**Solution**: Ensure timestep indices are sequential:
```python
import re

def extract_timestep_indices(columns, feature_name):
    pattern = f"{feature_name}_.*_(\\d+)"
    indices = []
    for col in columns:
        match = re.search(pattern, col)
        if match:
            indices.append(int(match.group(1)))
    return sorted(indices)

# Check timestep indices
indices = extract_timestep_indices(df.columns, 'pose')
print(f"Timestep indices: {indices}")
print(f"Expected range: {list(range(1, len(indices) + 1))}")
```

### Debugging Tips

1. **Start Small**: Test with a subset of your data first
2. **Check Data Types**: Ensure numerical columns are float/int, not object
3. **Validate Incrementally**: Test each feature configuration separately
4. **Use Verbose Output**: Enable debugging in your conversion functions

```python
# Debug mode example
def debug_dataframe_conversion(df, features_config):
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame dtypes:\n{df.dtypes}")
    
    for feature_name in features_config.keys():
        feature_cols = [col for col in df.columns if col.startswith(feature_name)]
        print(f"\nFeature '{feature_name}' columns: {len(feature_cols)}")
        print(f"Sample columns: {feature_cols[:3]}...")
        
        if feature_cols:
            sample_data = df[feature_cols[0]].head()
            print(f"Sample data: {sample_data}")
```

---

## Next Steps

- **[ROS To TCT Bag Usage Guide](rosbag_usage.md)** - Learn to extract trajectory data from ROS bags

---

## Documentation
- [Landing page](../README.md#_trajectory-container-tools_)
- [Overview and Core concept](README.md#trajectory-container-tools-documentation)
  - ↳ [Post-Processing Callbacks Guide](./post_processing_callbacks.md#post-processing-callbacks-in-tct)
  - ↳ [TCT Direct Instantiation Guide](direct_instantiation.md) - Create trajectory containers directly
  - ↳ [ROS To TCT Bag Usage Guide](rosbag_usage.md) - Learn to extract trajectory data from ROS bags
  - ↳ [Timestamp Utilities Guide](timestamp_utilities.md) - Advanced timestamp operations
- Interactive Jupyter notebook examples:
    - [Direct Instanciation Usage Examples](../notebooks/direct_instanciation_usage_example.ipynb) - Direct trajectory
      container instantiation
    - [ROS Bag Usage Examples](../notebooks/rosbag_usage_example.ipynb) - Extract trajectory data from ROS bags
    - [DataFrame Usage Examples](../notebooks/dataframe_usage_example.ipynb) - Convert pandas DataFrames to trajectory
      containers

