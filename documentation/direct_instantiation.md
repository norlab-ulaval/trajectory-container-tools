# Direct Instantiation Guide

This guide covers how to create trajectory containers directly from data arrays using Trajectory Container Tools (TCT).

## 📚 Table of Contents

- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Available Dataclasses](#available-dataclasses)
- [Custom Dataclasses](#custom-dataclasses)
- [Advanced Examples](#advanced-examples)
- [Data Validation](#data-validation)
- [Integration Patterns](#integration-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Direct instantiation allows you to create trajectory containers from raw data arrays (NumPy arrays, lists, etc.). This is ideal for:
- Creating synthetic trajectory data for testing
- Converting data from custom formats or APIs
- Building trajectory containers within algorithms
- Integrating with existing data processing pipelines
- Creating trajectory data for simulation environments

## Basic Usage

### 1. Import Required Modules

```python
import numpy as np
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    BaseReverseAxisTrajectoryDataclass
)
from trajectory_container_tools.trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass
)
```

### 2. Create Basic Trajectory Container

```python
# Generate sample trajectory data
timesteps = 100
x = np.linspace(0, 10, timesteps)
y = np.sin(x)
timestamps = np.arange(timesteps) * 0.1  # 10 Hz sampling

# Create trajectory container
trajectory = BaseTrajectoryDataclass(
        x=x,
        y=y,
        timestamps=timestamps
        )

print(f"Trajectory length: {trajectory.trajectory_len}")
print(f"Available dimensions: {trajectory.get_dimension_names()}")
print(f"Data shapes: x={trajectory.x.shape}, y={trajectory.y.shape}")
```

### 3. Access Trajectory Data

```python
# Access individual dimensions
x_positions = trajectory.x
y_positions = trajectory.y
time_stamps = trajectory.timestamps

# Slice trajectory
partial_trajectory = trajectory[10:50]  # Get timesteps 10-49
print(f"Partial trajectory length: {partial_trajectory.trajectory_len}")

# Iterate through trajectory
for i, (x_val, y_val) in enumerate(trajectory):
    if i < 5:  # Print first 5 points
        print(f"Point {i}: x={x_val:.3f}, y={y_val:.3f}")
```

## Available Dataclasses

### Base Trajectory Dataclasses

#### `BaseTrajectoryDataclass`
Standard trajectory container with time as the last axis.

```python
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import BaseTrajectoryDataclass

# Single trajectory (1D arrays)
trajectory = BaseTrajectoryDataclass(
    x=np.array([0, 1, 2, 3, 4]),
    y=np.array([0, 1, 0, -1, 0]),
    timestamps=np.array([0.0, 0.1, 0.2, 0.3, 0.4])
)

# Batch trajectories (2D arrays: [batch_size, time_steps])
batch_size, time_steps = 10, 50
batch_trajectory = BaseTrajectoryDataclass(
    x=np.random.randn(batch_size, time_steps),
    y=np.random.randn(batch_size, time_steps),
    timestamps=np.tile(np.arange(time_steps) * 0.1, (batch_size, 1))
)
```

#### `BaseReverseAxisTrajectoryDataclass`
Trajectory container with time as the first axis.

```python
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import BaseReverseAxisTrajectoryDataclass

# Time-first trajectory (time_steps, batch_size)
time_first_trajectory = BaseReverseAxisTrajectoryDataclass(
    x=np.random.randn(50, 10),  # [time_steps, batch_size]
    y=np.random.randn(50, 10),
    timestamps=np.arange(50) * 0.1
)
```

#### `NestedBaseTrajectoryDataclass`
For complex nested trajectory structures.

```python
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass

# Nested trajectory with multiple levels
nested_trajectory = NestedBaseTrajectoryDataclass(
    pose_x=np.random.randn(5, 20),  # 5 robots, 20 timesteps
    pose_y=np.random.randn(5, 20),
    timestamps=np.tile(np.arange(20) * 0.1, (5, 1))
)
```

### Specialized Dataclasses

#### ERLL Trajectories
```python
from trajectory_container_tools.trj_dataclasses.erll_trajectory_dataclass import ErllTrajectoryDataclass

erll_trajectory = ErllTrajectoryDataclass(
    x=np.array([0, 1, 2]),
    y=np.array([0, 1, 2]), 
    theta=np.array([0, 0.1, 0.2]),
    timestamps=np.array([0, 0.1, 0.2])
)
```

#### F1/10 Racing Trajectories
```python
from trajectory_container_tools.trj_dataclasses.f110_gym_trajectory_dataclass import F110GymTrajectoryDataclass

f110_trajectory = F110GymTrajectoryDataclass(
    x=np.array([0, 1, 2]),
    y=np.array([0, 0.5, 1]),
    theta=np.array([0, 0.1, 0.2]),
    velocity=np.array([0, 5, 10]),
    timestamps=np.array([0, 0.1, 0.2])
)
```

#### Math Gymnasium Trajectories
```python
from trajectory_container_tools.trj_dataclasses.math_gymnasium_trajectory_dataclass import MathGymnasiumTrajectoryDataclass

mg_trajectory = MathGymnasiumTrajectoryDataclass(
    state=np.random.randn(100, 4),  # 4D state space
    action=np.random.randn(100, 2), # 2D action space
    timestamps=np.arange(100) * 0.01
)
```

## Custom Dataclasses

### Creating Custom Trajectory Dataclasses

```python
from dataclasses import dataclass
import numpy as np

@dataclass
class RobotTrajectoryDataclass(BaseTrajectoryDataclass):
    """Custom trajectory dataclass for robot navigation"""
    x: np.ndarray
    y: np.ndarray
    theta: np.ndarray
    velocity: np.ndarray
    steering_angle: np.ndarray
    
    @classmethod
    def get_dimension_names(cls):
        return ['x', 'y', 'theta', 'velocity', 'steering_angle']
    
    def post_init_feature_callback(self, feature_name: str):
        """Custom processing after initialization"""
        if feature_name == 'theta':
            # Wrap angles to [-pi, pi]
            theta = getattr(self, feature_name)
            wrapped_theta = np.arctan2(np.sin(theta), np.cos(theta))
            setattr(self, feature_name, wrapped_theta)
        
        super().post_init_feature_callback(feature_name)

# Use custom dataclass
robot_traj = RobotTrajectoryDataclass(
    x=np.linspace(0, 10, 100),
    y=np.sin(np.linspace(0, 2*np.pi, 100)),
    theta=np.linspace(0, 4*np.pi, 100),  # Will be wrapped to [-pi, pi]
    velocity=np.ones(100) * 2.5,
    steering_angle=np.random.randn(100) * 0.1,
    timestamps=np.arange(100) * 0.1
)
```

### Multi-Feature Custom Dataclass

```python
@dataclass 
class MultiSensorTrajectoryDataclass(AbstractMultifeatureDataclass):
    """Container for multi-sensor trajectory data"""
    pose: BaseTrajectoryDataclass
    velocity: BaseTrajectoryDataclass
    imu: BaseTrajectoryDataclass
    lidar: BaseTrajectoryDataclass
    
    def __post_init__(self):
        super().__post_init__()
        
    def summary(self):
        print(f"Multi-sensor trajectory container:")
        print(f"  - Pose: {self.pose.trajectory_len} timesteps")
        print(f"  - Velocity: {self.velocity.trajectory_len} timesteps") 
        print(f"  - IMU: {self.imu.trajectory_len} timesteps")
        print(f"  - Lidar: {self.lidar.trajectory_len} timesteps")

# Create individual trajectory components
pose_data = BaseTrajectoryDataclass(
    x=np.random.randn(100), y=np.random.randn(100),
    timestamps=np.arange(100) * 0.1
)

velocity_data = BaseTrajectoryDataclass(
    vx=np.random.randn(100), vy=np.random.randn(100),
    timestamps=np.arange(100) * 0.1
)

imu_data = BaseTrajectoryDataclass(
    accel_x=np.random.randn(100), accel_y=np.random.randn(100), 
    gyro_z=np.random.randn(100),
    timestamps=np.arange(100) * 0.1
)

lidar_data = BaseTrajectoryDataclass(
    range_front=np.random.uniform(0.1, 10, 100),
    range_left=np.random.uniform(0.1, 10, 100),
    range_right=np.random.uniform(0.1, 10, 100),
    timestamps=np.arange(100) * 0.1
)

# Combine into multi-feature container
multi_sensor_traj = MultiSensorTrajectoryDataclass(
    pose=pose_data,
    velocity=velocity_data, 
    imu=imu_data,
    lidar=lidar_data
)

multi_sensor_traj.summary()
```

## Advanced Examples

### Example 1: Synthetic Robot Navigation Data

```python
import numpy as np
import matplotlib.pyplot as plt

def generate_robot_navigation_trajectory(duration=10.0, dt=0.1):
    """Generate synthetic robot navigation trajectory"""
    
    timesteps = int(duration / dt)
    t = np.linspace(0, duration, timesteps)
    
    # Generate circular trajectory with noise
    radius = 5.0
    angular_freq = 0.5
    
    # Position (circular path with noise)
    x = radius * np.cos(angular_freq * t) + np.random.normal(0, 0.1, timesteps)
    y = radius * np.sin(angular_freq * t) + np.random.normal(0, 0.1, timesteps) 
    
    # Orientation (tangent to circle)
    theta = angular_freq * t + np.pi/2 + np.random.normal(0, 0.05, timesteps)
    
    # Velocity (computed from position)
    vx = np.gradient(x, dt)
    vy = np.gradient(y, dt)
    velocity = np.sqrt(vx**2 + vy**2)
    
    # Angular velocity  
    angular_velocity = np.gradient(theta, dt)
    
    # Control commands (with realistic constraints)
    linear_cmd = np.clip(velocity + np.random.normal(0, 0.1, timesteps), 0, 3.0)
    angular_cmd = np.clip(angular_velocity + np.random.normal(0, 0.05, timesteps), -1.0, 1.0)
    
    # Create trajectory container
    trajectory = BaseTrajectoryDataclass(
        # State
        x=x, y=y, theta=theta,
        # Velocity  
        vx=vx, vy=vy, velocity=velocity, angular_velocity=angular_velocity,
        # Commands
        linear_cmd=linear_cmd, angular_cmd=angular_cmd,
        # Time
        timestamps=t
    )
    
    return trajectory

# Generate and visualize trajectory
nav_trajectory = generate_robot_navigation_trajectory(duration=20.0)

plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.plot(nav_trajectory.x, nav_trajectory.y, 'b-', alpha=0.7)
plt.xlabel('X Position (m)')
plt.ylabel('Y Position (m)')
plt.title('Robot Trajectory')
plt.axis('equal')
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot(nav_trajectory.timestamps, nav_trajectory.velocity, 'g-')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Velocity Profile')
plt.grid(True)

plt.subplot(2, 2, 3)
plt.plot(nav_trajectory.timestamps, nav_trajectory.angular_velocity, 'r-')
plt.xlabel('Time (s)')
plt.ylabel('Angular Velocity (rad/s)')
plt.title('Angular Velocity Profile')
plt.grid(True)

plt.subplot(2, 2, 4)
plt.plot(nav_trajectory.timestamps, nav_trajectory.linear_cmd, 'c-', label='Linear')
plt.plot(nav_trajectory.timestamps, nav_trajectory.angular_cmd, 'm-', label='Angular')
plt.xlabel('Time (s)')
plt.ylabel('Command')
plt.title('Control Commands')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

print(f"Generated trajectory with {nav_trajectory.trajectory_len} timesteps")
print(f"Duration: {nav_trajectory.timestamps[-1]:.1f} seconds")
```

### Example 2: Batch Trajectory Processing

```python
def generate_batch_trajectories(num_trajectories=10, timesteps=100):
    """Generate batch of robot trajectories with different parameters"""
    
    trajectories = []
    
    for i in range(num_trajectories):
        # Randomize trajectory parameters
        radius = np.random.uniform(2.0, 8.0)
        freq = np.random.uniform(0.1, 1.0)
        noise_level = np.random.uniform(0.05, 0.2)
        duration = np.random.uniform(8.0, 15.0)
        
        t = np.linspace(0, duration, timesteps)
        
        # Generate trajectory
        x = radius * np.cos(freq * t) + np.random.normal(0, noise_level, timesteps)
        y = radius * np.sin(freq * t) + np.random.normal(0, noise_level, timesteps)
        theta = freq * t + np.pi/2
        
        trajectory = BaseTrajectoryDataclass(
            x=x, y=y, theta=theta,
            timestamps=t,
            trajectory_id=np.full(timesteps, i)  # Add trajectory ID
        )
        
        trajectories.append(trajectory)
    
    return trajectories

# Generate batch trajectories
batch_trajectories = generate_batch_trajectories(num_trajectories=5, timesteps=200)

# Visualize batch
plt.figure(figsize=(10, 8))
colors = plt.cm.viridis(np.linspace(0, 1, len(batch_trajectories)))

for i, traj in enumerate(batch_trajectories):
    plt.plot(traj.x, traj.y, color=colors[i], alpha=0.7, 
             label=f'Trajectory {i+1}')

plt.xlabel('X Position (m)')
plt.ylabel('Y Position (m)')
plt.title('Batch Robot Trajectories')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.show()

# Analyze batch statistics
x_ranges = [np.ptp(traj.x) for traj in batch_trajectories]  # Peak-to-peak
y_ranges = [np.ptp(traj.y) for traj in batch_trajectories]

print(f"X range statistics: mean={np.mean(x_ranges):.2f}, std={np.std(x_ranges):.2f}")
print(f"Y range statistics: mean={np.mean(y_ranges):.2f}, std={np.std(y_ranges):.2f}")
```

### Example 3: Converting External Data Format

```python
def convert_external_trajectory_data(external_data_dict):
    """Convert external trajectory data format to TCT format"""
    
    # Assume external format:
    # {
    #   'positions': [[x1, y1], [x2, y2], ...],
    #   'orientations': [theta1, theta2, ...], 
    #   'velocities': [v1, v2, ...],
    #   'time': [t1, t2, ...]
    # }
    
    positions = np.array(external_data_dict['positions'])
    orientations = np.array(external_data_dict['orientations'])
    velocities = np.array(external_data_dict['velocities'])
    timestamps = np.array(external_data_dict['time'])
    
    # Extract position components
    x = positions[:, 0]
    y = positions[:, 1]
    
    # Create trajectory container
    trajectory = BaseTrajectoryDataclass(
        x=x,
        y=y, 
        theta=orientations,
        velocity=velocities,
        timestamps=timestamps
    )
    
    return trajectory

# Example external data
external_data = {
    'positions': [[0, 0], [1, 1], [2, 0], [3, -1], [4, 0]],
    'orientations': [0, 0.785, 1.57, -0.785, 0],
    'velocities': [0, 1.414, 1.0, 1.414, 1.0],
    'time': [0.0, 1.0, 2.0, 3.0, 4.0]
}

converted_trajectory = convert_external_trajectory_data(external_data)
print(f"Converted trajectory: {converted_trajectory.trajectory_len} points")
print(f"Position range: x=[{converted_trajectory.x.min():.1f}, {converted_trajectory.x.max():.1f}]")
```

## Data Validation

### Built-in Validation

TCT automatically validates:
- Array shape consistency across dimensions
- Timestamp monotonicity
- Data type compatibility

### Custom Validation

```python
@dataclass
class ValidatedTrajectoryDataclass(BaseTrajectoryDataclass):
    """Trajectory dataclass with custom validation"""
    
    def post_init_feature_callback(self, feature_name: str):
        """Custom validation for each feature"""
        feature = getattr(self, feature_name)
        
        if isinstance(feature, np.ndarray):
            # Check for NaN values
            if np.any(np.isnan(feature)):
                raise ValueError(f"NaN values detected in {feature_name}")
            
            # Check for infinite values  
            if np.any(np.isinf(feature)):
                raise ValueError(f"Infinite values detected in {feature_name}")
            
            # Feature-specific validation
            if feature_name == 'x' and (np.any(np.abs(feature) > 1000)):
                raise ValueError(f"X positions out of reasonable range: {feature_name}")
            
            if feature_name == 'velocity' and (np.any(feature < 0)):
                raise ValueError(f"Negative velocities detected: {feature_name}")
            
            if feature_name == 'timestamps':
                # Check monotonicity
                if not np.all(np.diff(feature) >= 0):
                    raise ValueError("Timestamps are not monotonic")
                
                # Check for reasonable time values
                if np.any(feature < 0):
                    raise ValueError("Negative timestamps detected")
        
        super().post_init_feature_callback(feature_name)

# Test validation
try:
    valid_trajectory = ValidatedTrajectoryDataclass(
        x=np.array([0, 1, 2, 3]),
        y=np.array([0, 1, 0, -1]),
        velocity=np.array([0, 1, 1, 1]),  # All positive
        timestamps=np.array([0, 1, 2, 3])  # Monotonic
    )
    print("✓ Trajectory validation passed")
    
except ValueError as e:
    print(f"✗ Validation failed: {e}")

# Test with invalid data
try:
    invalid_trajectory = ValidatedTrajectoryDataclass(
        x=np.array([0, 1, 2, 3]),
        y=np.array([0, 1, 0, -1]), 
        velocity=np.array([0, -1, 1, 1]),  # Contains negative velocity
        timestamps=np.array([0, 1, 2, 3])
    )
except ValueError as e:
    print(f"✓ Validation correctly caught error: {e}")
```

### Data Preprocessing and Cleaning

```python
@dataclass
class CleanedTrajectoryDataclass(BaseTrajectoryDataclass):
    """Trajectory dataclass with automatic data cleaning"""
    
    def post_init_feature_callback(self, feature_name: str):
        """Clean and preprocess data"""
        feature = getattr(self, feature_name)
        
        if isinstance(feature, np.ndarray):
            original_feature = feature.copy()
            
            # Remove NaN values (interpolate)
            if np.any(np.isnan(feature)):
                print(f"Interpolating NaN values in {feature_name}")
                nan_mask = np.isnan(feature)
                valid_indices = np.where(~nan_mask)[0]
                if len(valid_indices) > 1:
                    feature[nan_mask] = np.interp(
                        np.where(nan_mask)[0], 
                        valid_indices, 
                        feature[valid_indices]
                    )
            
            # Clip outliers (3-sigma rule)
            if feature_name in ['x', 'y', 'velocity']:
                mean_val = np.mean(feature)
                std_val = np.std(feature)
                outlier_mask = np.abs(feature - mean_val) > 3 * std_val
                
                if np.any(outlier_mask):
                    print(f"Clipping {np.sum(outlier_mask)} outliers in {feature_name}")
                    feature[outlier_mask] = np.clip(
                        feature[outlier_mask],
                        mean_val - 3*std_val,
                        mean_val + 3*std_val
                    )
            
            # Smooth data (optional)
            if feature_name in ['x', 'y'] and len(feature) > 5:
                from scipy.ndimage import uniform_filter1d
                feature = uniform_filter1d(feature, size=3)
            
            # Update the feature if modified
            if not np.array_equal(feature, original_feature):
                setattr(self, feature_name, feature)
        
        super().post_init_feature_callback(feature_name)

# Test data cleaning
noisy_data = BaseTrajectoryDataclass(
    x=np.array([0, 1, np.nan, 3, 100, 5]),  # Contains NaN and outlier
    y=np.array([0, 1, 2, np.nan, 4, 5]),    # Contains NaN
    timestamps=np.array([0, 1, 2, 3, 4, 5])
)

cleaned_trajectory = CleanedTrajectoryDataclass(
    x=noisy_data.x.copy(),
    y=noisy_data.y.copy(), 
    timestamps=noisy_data.timestamps
)

print("Original x:", noisy_data.x)
print("Cleaned x:", cleaned_trajectory.x)
```

## Integration Patterns

### Factory Functions

```python
def create_trajectory_from_config(config):
    """Create trajectory from configuration dictionary"""
    
    if config['type'] == 'circular':
        t = np.linspace(0, config['duration'], config['timesteps'])
        x = config['radius'] * np.cos(config['frequency'] * t)
        y = config['radius'] * np.sin(config['frequency'] * t)
        
        return BaseTrajectoryDataclass(x=x, y=y, timestamps=t)
        
    elif config['type'] == 'linear':
        t = np.linspace(0, config['duration'], config['timesteps'])
        x = config['velocity'] * t * np.cos(config['direction'])
        y = config['velocity'] * t * np.sin(config['direction'])
        
        return BaseTrajectoryDataclass(x=x, y=y, timestamps=t)
    
    else:
        raise ValueError(f"Unknown trajectory type: {config['type']}")

# Usage
circular_config = {
    'type': 'circular',
    'radius': 3.0,
    'frequency': 0.5,
    'duration': 10.0,
    'timesteps': 100
}

linear_config = {
    'type': 'linear',
    'velocity': 2.0,
    'direction': np.pi/4,  # 45 degrees
    'duration': 5.0,
    'timesteps': 50
}

circular_traj = create_trajectory_from_config(circular_config)
linear_traj = create_trajectory_from_config(linear_config)
```

### Algorithm Integration

```python
class TrajectoryProcessor:
    """Example processor that works with trajectory containers"""
    
    def __init__(self):
        self.processed_trajectories = []
    
    def smooth_trajectory(self, trajectory, window_size=5):
        """Apply smoothing filter to trajectory"""
        from scipy.ndimage import uniform_filter1d
        
        smoothed_x = uniform_filter1d(trajectory.x, size=window_size)
        smoothed_y = uniform_filter1d(trajectory.y, size=window_size)
        
        return BaseTrajectoryDataclass(
            x=smoothed_x,
            y=smoothed_y,
            timestamps=trajectory.timestamps
        )
    
    def resample_trajectory(self, trajectory, new_frequency=10.0):
        """Resample trajectory to new frequency"""
        old_timestamps = trajectory.timestamps
        duration = old_timestamps[-1] - old_timestamps[0]
        new_timesteps = int(duration * new_frequency) + 1
        new_timestamps = np.linspace(old_timestamps[0], old_timestamps[-1], new_timesteps)
        
        # Interpolate trajectory data
        new_x = np.interp(new_timestamps, old_timestamps, trajectory.x)
        new_y = np.interp(new_timestamps, old_timestamps, trajectory.y)
        
        return BaseTrajectoryDataclass(
            x=new_x,
            y=new_y,
            timestamps=new_timestamps
        )
    
    def compute_trajectory_metrics(self, trajectory):
        """Compute trajectory metrics"""
        # Path length
        dx = np.diff(trajectory.x)
        dy = np.diff(trajectory.y)
        path_length = np.sum(np.sqrt(dx**2 + dy**2))
        
        # Average velocity
        dt = np.diff(trajectory.timestamps)
        velocities = np.sqrt(dx**2 + dy**2) / dt
        avg_velocity = np.mean(velocities)
        
        # Bounding box
        x_range = trajectory.x.max() - trajectory.x.min()
        y_range = trajectory.y.max() - trajectory.y.min()
        
        return {
            'path_length': path_length,
            'average_velocity': avg_velocity,
            'x_range': x_range,
            'y_range': y_range,
            'duration': trajectory.timestamps[-1] - trajectory.timestamps[0]
        }

# Usage example
processor = TrajectoryProcessor()

# Generate test trajectory
test_traj = BaseTrajectoryDataclass(
    x=np.random.randn(100).cumsum(),
    y=np.random.randn(100).cumsum(),
    timestamps=np.arange(100) * 0.1
)

# Process trajectory
smoothed_traj = processor.smooth_trajectory(test_traj, window_size=5)
resampled_traj = processor.resample_trajectory(smoothed_traj, new_frequency=20.0)
metrics = processor.compute_trajectory_metrics(resampled_traj)

print("Trajectory metrics:")
for key, value in metrics.items():
    print(f"  {key}: {value:.3f}")
```

## Best Practices

### 1. Data Organization

```python
# Use descriptive field names
good_trajectory = BaseTrajectoryDataclass(
    robot_position_x=x_data,
    robot_position_y=y_data,
    robot_orientation=theta_data,
    timestamps=time_data
)

# Group related data logically
class RobotStateTrajectory(BaseTrajectoryDataclass):
    # Position
    x: np.ndarray
    y: np.ndarray 
    theta: np.ndarray
    
    # Velocity  
    vx: np.ndarray
    vy: np.ndarray
    omega: np.ndarray
    
    # Commands
    linear_cmd: np.ndarray
    angular_cmd: np.ndarray
```

### 2. Memory Efficiency

```python
# Use appropriate data types
trajectory = BaseTrajectoryDataclass(
    x=np.array(x_data, dtype=np.float32),  # Use float32 if precision allows
    y=np.array(y_data, dtype=np.float32),
    timestamps=np.array(time_data, dtype=np.float64)  # Keep high precision for time
)

# For large datasets, consider memory mapping
large_data = np.memmap('trajectory_data.dat', dtype='float32', mode='w+', shape=(1000000, 3))
# ... populate data ...

large_trajectory = BaseTrajectoryDataclass(
    x=large_data[:, 0],
    y=large_data[:, 1], 
    theta=large_data[:, 2],
    timestamps=np.arange(1000000) * 0.001
)
```

### 3. Error Handling

```python
def safe_trajectory_creation(data_dict):
    """Safely create trajectory with error handling"""
    try:
        # Validate inputs
        required_fields = ['x', 'y', 'timestamps']
        for field in required_fields:
            if field not in data_dict:
                raise ValueError(f"Missing required field: {field}")
            
            if not isinstance(data_dict[field], np.ndarray):
                data_dict[field] = np.array(data_dict[field])
        
        # Check array lengths
        lengths = [len(data_dict[field]) for field in required_fields]
        if not all(length == lengths[0] for length in lengths):
            raise ValueError("All data arrays must have the same length")
        
        # Create trajectory
        trajectory = BaseTrajectoryDataclass(**data_dict)
        return trajectory, None
        
    except Exception as e:
        return None, str(e)

# Usage
data = {'x': [0, 1, 2], 'y': [0, 1, 0], 'timestamps': [0, 1, 2]}
trajectory, error = safe_trajectory_creation(data)

if trajectory:
    print("✓ Trajectory created successfully")
else:
    print(f"✗ Error: {error}")
```

### 4. Documentation and Metadata

```python
@dataclass
class DocumentedTrajectoryDataclass(BaseTrajectoryDataclass):
    """Well-documented trajectory dataclass"""
    x: np.ndarray  # Robot X position in meters (world frame)
    y: np.ndarray  # Robot Y position in meters (world frame)  
    theta: np.ndarray  # Robot orientation in radians [-π, π]
    velocity: np.ndarray  # Linear velocity in m/s

    # Declare the Metadata fields
    robot_id: str = "robot_1"
    experiment_date: str = ""
    environment: str = ""
    notes: str = ""

    # Register the new metadats fields by extending the `trajectory_metadata_field` class method 
    @classmethod
    def trajectory_metadata_field(cls) -> List[str]:
        return super().trajectory_metadata_field() + [
                "robot_id",
                "experiment_date",
                "environment",
                "notes",
                ]

    def get_metadata(self):
        """Return trajectory metadata"""
        return {
                'robot_id':        self.robot_id,
                'experiment_date': self.experiment_date,
                'environment':     self.environment,
                'notes':           self.notes,
                'duration':        self.timestamps[-1] - self.timestamps[0],
                'sample_rate':     len(self.timestamps) / (self.timestamps[-1] - self.timestamps[0]),
                'num_samples':     self.trajectory_len
                }


# Create documented trajectory
documented_traj = DocumentedTrajectoryDataclass(
        x=np.random.randn(100),
        y=np.random.randn(100),
        theta=np.random.randn(100),
        velocity=np.abs(np.random.randn(100)),
        timestamps=np.arange(100) * 0.1,
        robot_id="robot_alpha",
        experiment_date="2024-01-15",
        environment="indoor_lab",
        notes="Navigation experiment with obstacles"
        )

print("Trajectory metadata:")
for key, value in documented_traj.get_metadata().items():
    print(f"  {key}: {value}")
```

## Troubleshooting

### Common Issues

#### 1. Array Shape Mismatch
```
Error: Arrays have inconsistent shapes
```

**Solution:**
```python
# Check array shapes before creating trajectory
print(f"x shape: {x.shape}")
print(f"y shape: {y.shape}")
print(f"timestamps shape: {timestamps.shape}")

# Ensure all arrays have same length
min_length = min(len(x), len(y), len(timestamps))
trajectory = BaseTrajectoryDataclass(
    x=x[:min_length],
    y=y[:min_length],
    timestamps=timestamps[:min_length]
)
```

#### 2. Data Type Issues
```
Error: Cannot convert to numpy array
```

**Solution:**
```python
# Convert data to numpy arrays explicitly
trajectory = BaseTrajectoryDataclass(
    x=np.array(x_data, dtype=np.float64),
    y=np.array(y_data, dtype=np.float64),
    timestamps=np.array(time_data, dtype=np.float64)
)
```

---

## Next Steps

- **[DataFrame To TCT Usage Guide](dataframe_usage.md)** - Convert pandas DataFrames to trajectory containers
- **[ROS Bag To TCT Usage Guide](rosbag_usage.md)** - Extract trajectory data from ROS bags
- **[Jupyter Notebook Examples](../notebooks/dataclass_usage_example.ipynb)** - Interactive direct instantiation examples

---

*For more help, see the [main documentation](README.md) or check the [Jupyter notebook examples](../notebooks/).*
