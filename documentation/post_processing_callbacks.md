# Post-Processing Callbacks in TCT

## Overview

Trajectory Container Tools (TCT) provides a powerful post-processing callback system that allows you to execute custom logic during trajectory dataclass instantiation. This system is built into the `AbstractTrajectoryCommon` base class and is automatically available to all trajectory containers.

## The Three Callback Methods

TCT provides three callback hooks that execute at different stages of the `__post_init__` method:

### 1. `on_begin_post_init_callback()`

**When it executes:** At the very beginning of `__post_init__`, before any feature processing.

**Scope:** Has access to all fields (including internal and non-trajectory fields).

**Use cases:**
- Initialize computed fields that other callbacks will use
- Validate or transform input data before processing
- Set up metadata or configuration
- Perform global data preprocessing

**Example:**

```python
from dataclasses import dataclass
import numpy as np
import trajectory_container_tools as tct


@dataclass
class TrajectoryWithPreprocessing(tct.BaseTrajectoryFeature):
    x: np.ndarray
    y: np.ndarray

    def on_begin_post_init_callback(self):
        """Normalize coordinates at the start."""
        # Center the trajectory around origin
        x_mean = np.mean(self.x)
        y_mean = np.mean(self.y)
        self.set_dynamic_attribute('x', self.x - x_mean)
        self.set_dynamic_attribute('y', self.y - y_mean)

        # Store the offset for later use
        self.set_dynamic_attribute('offset_x', x_mean)
        self.set_dynamic_attribute('offset_y', y_mean)
```

### 2. `post_init_feature_callback(feature_name: str)`

**When it executes:** Once for each feature field in the dataclass.

**Scope:** Only processes fields that are NOT marked in `_dataclass_internal_field()` or `non_trajectory_field()`.

**Parameters:**
- `feature_name` (str): The name of the current feature being processed

**Use cases:**
- Feature-specific transformations
- Create derived features based on existing ones
- Apply per-feature validation
- Generate feature-specific metadata

**Example:**

```python
from dataclasses import dataclass
import numpy as np
import trajectory_container_tools as tct


@dataclass
class TrajectoryWithDerivedFeatures(tct.BaseTrajectoryFeature):
    x: np.ndarray
    y: np.ndarray
    velocity: np.ndarray

    def post_init_feature_callback(self, feature_name: str):
        """Create derivative and cumulative features."""
        feature = self.get_dynamic_attribute(feature_name)

        if isinstance(feature, np.ndarray):
            # Create rate of change for each feature
            if feature_name in ['x', 'y', 'velocity']:
                rate = np.diff(feature, prepend=feature[0])
                self.set_dynamic_attribute(f"{feature_name}_rate", rate)

            # Create cumulative sum for position features
            if feature_name in ['x', 'y']:
                cumsum = np.cumsum(feature)
                self.set_dynamic_attribute(f"{feature_name}_cumsum", cumsum)
```

### 3. `on_exit_post_init_callback()`

**When it executes:** At the very end of `__post_init__`, after all feature processing is complete.

**Scope:** Has access to all fields, including any dynamically created fields from previous callbacks.

**Use cases:**
- Final validation and assertions
- Compute aggregate statistics or properties
- Create features that depend on multiple processed fields
- Cleanup or finalization tasks

**Example:**

```python
from dataclasses import dataclass
import numpy as np
import trajectory_container_tools as tct


@dataclass
class TrajectoryWithStatistics(tct.BaseTrajectoryFeature):
    x: np.ndarray
    y: np.ndarray
    velocity: np.ndarray

    def on_exit_post_init_callback(self):
        """Compute trajectory statistics and validate data."""
        # Compute total distance
        dx = np.diff(self.x, prepend=self.x[0])
        dy = np.diff(self.y, prepend=self.y[0])
        distances = np.sqrt(dx ** 2 + dy ** 2)
        self.set_dynamic_attribute('distance_per_step', distances)
        self.set_dynamic_attribute('total_distance', np.sum(distances))

        # Compute trajectory bounds
        self.set_dynamic_attribute('x_min', np.min(self.x))
        self.set_dynamic_attribute('x_max', np.max(self.x))
        self.set_dynamic_attribute('y_min', np.min(self.y))
        self.set_dynamic_attribute('y_max', np.max(self.y))

        # Validate trajectory length
        assert len(self.x) > 0, "Trajectory must have at least one point"
        assert len(self.velocity) == len(self.x), "Velocity and position arrays must have same length"
```

## Execution Flow

The callbacks are executed in the following order during instantiation:

```
1. Dataclass __init__
   ↓
2. __post_init__ begins
   ↓
3. on_begin_post_init_callback()        ← Runs once
   ↓
4. For each feature field:
   ↓
   post_init_feature_callback(feature)   ← Runs N times
   ↓
5. on_exit_post_init_callback()         ← Runs once
   ↓
6. __post_init__ ends
```

## Dynamic Field Management

All callbacks have access to helper methods for dynamic field manipulation:

### `get_dynamic_attribute(feature_name: str) -> Any`

Retrieve the value of any attribute from the dataclass.

```python
value = self.pose.pose.position.get_dynamic_attribute("x")
```

Access nested attributes using dot notation (useful for ROS message structures).

```python
# For nested structures like NavMsgsOdometry
position_x = self.get_dynamic_attribute("pose.pose.position.x")
```

### `set_dynamic_attribute(feature_name: str, value: Any) -> None`

Create or update an attribute on the dataclass.

```python
self.set_dynamic_attribute("x_squared", self.x ** 2)
```

Create or update nested attributes using dot notation (useful for ROS message structures).

```python
self.set_dynamic_attribute("pose.pose.position.x", 10)
```

## Advanced Example: Complete Trajectory Post-Processing

Here's a comprehensive example combining all three callbacks:

```python
from dataclasses import dataclass
import numpy as np
import trajectory_container_tools as tct


@dataclass
class AdvancedTrajectory(tct.BaseTrajectoryFeature):
    x: np.ndarray
    y: np.ndarray
    velocity: np.ndarray
    steering: np.ndarray

    def on_begin_post_init_callback(self):
        """Initialize processing and validate input."""
        # Ensure all arrays have consistent length
        lengths = [len(self.x), len(self.y), len(self.velocity), len(self.steering)]
        assert len(set(lengths)) == 1, f"Inconsistent array lengths: {lengths}"

        # Store trajectory metadata
        self.set_dynamic_attribute('trajectory_length', len(self.x))

        # Initialize a processing flag
        self.set_dynamic_attribute('_callbacks_executed', True)

    def post_init_feature_callback(self, feature_name: str):
        """Create statistical features for each trajectory dimension."""
        feature = self.get_dynamic_attribute(feature_name)

        if isinstance(feature, np.ndarray) and len(feature) > 0:
            # Compute statistics
            stats = {
                    f"{feature_name}_mean": np.mean(feature),
                    f"{feature_name}_std":  np.std(feature),
                    f"{feature_name}_min":  np.min(feature),
                    f"{feature_name}_max":  np.max(feature),
                    }

            # Only create rate of change for physical quantities
            if feature_name in ['x', 'y', 'velocity', 'steering']:
                rate = np.diff(feature, prepend=feature[0])
                stats[f"{feature_name}_rate"] = rate

            # Set all computed statistics
            for stat_name, stat_value in stats.items():
                self.set_dynamic_attribute(stat_name, stat_value)

    def on_exit_post_init_callback(self):
        """Compute derived trajectory properties."""
        # Compute path curvature
        dx = np.diff(self.x, prepend=self.x[0])
        dy = np.diff(self.y, prepend=self.y[0])

        # Distance traveled per step
        step_distances = np.sqrt(dx ** 2 + dy ** 2)
        self.set_dynamic_attribute('step_distances', step_distances)
        self.set_dynamic_attribute('total_distance', np.sum(step_distances))

        # Heading angle (direction of travel)
        heading = np.arctan2(dy, dx)
        self.set_dynamic_attribute('heading', heading)

        # Curvature (change in heading per unit distance)
        dheading = np.diff(heading, prepend=heading[0])
        curvature = dheading / (step_distances + 1e-6)  # Avoid division by zero
        self.set_dynamic_attribute('curvature', curvature)

        # Create trajectory quality metrics
        smoothness = np.std(curvature)
        self.set_dynamic_attribute('trajectory_smoothness', smoothness)

        # Final validation
        assert np.all(np.isfinite(self.x)), "x contains non-finite values"
        assert np.all(np.isfinite(self.y)), "y contains non-finite values"


# Usage
trajectory = AdvancedTrajectory(
        feature_name="advanced_example",
        x=np.linspace(0, 10, 100),
        y=np.sin(np.linspace(0, 2 * np.pi, 100)),
        velocity=np.ones(100) * 2.0,
        steering=np.linspace(-0.5, 0.5, 100),
        timesteps_indices=np.arange(100)
        )

# Access computed properties
print(f"Total distance: {trajectory.total_distance:.2f}")
print(f"Trajectory smoothness: {trajectory.trajectory_smoothness:.4f}")
print(f"Mean velocity: {trajectory.velocity_mean:.2f}")
print(f"Max curvature: {trajectory.curvature_max:.4f}")
```

## Best Practices

### 1. Keep Callbacks Focused

Each callback should have a clear, single responsibility:
- `on_begin_post_init_callback`: Setup and initialization
- `post_init_feature_callback`: Per-feature processing
- `on_exit_post_init_callback`: Finalization and validation

### 2. Use Appropriate Scope

- Use `post_init_feature_callback` for operations that should apply to each feature independently
- Use `on_begin_post_init_callback` or `on_exit_post_init_callback` for operations that need the full context

### 3. Avoid Heavy Computation in Callbacks

Callbacks execute during instantiation, which can slow down object creation. For expensive computations:
- Consider lazy evaluation using properties
- Cache results when possible
- Document performance implications

### 4. Handle Edge Cases

Always validate your assumptions:

```python
def post_init_feature_callback(self, feature_name: str):
    feature = self.get_dynamic_attribute(feature_name)
    
    # Check type before processing
    if isinstance(feature, np.ndarray):
        # Check for non-empty arrays
        if len(feature) > 0:
            # Safe to process
            pass
```

### 5. Document Your Callbacks

Make it clear what each callback does:
```python
def on_exit_post_init_callback(self):
    """
    Compute trajectory statistics and validate data integrity.
    
    Creates the following dynamic fields:
    - total_distance: Sum of Euclidean distances between consecutive points
    - heading: Direction of travel in radians
    - curvature: Rate of change of heading
    
    Raises:
        AssertionError: If trajectory contains non-finite values
    """
    # Implementation
```

## Use Cases by Domain

### Robotics Research
- Compute odometry-derived features (velocity, acceleration)
- Transform coordinate frames
- Synchronize multi-sensor data
- Validate trajectory feasibility

### Autonomous Systems
- Filter noisy sensor data
- Compute control metrics
- Validate safety constraints
- Generate trajectory predictions

### Machine Learning / RL
- Normalize features for neural networks
- Create observation-action pairs
- Compute reward signals
- Generate time-windowed features

### Data Analysis
- Compute trajectory statistics
- Detect anomalies
- Extract patterns
- Generate visualizations data

## Integration with Extractors

Callbacks work seamlessly with TCT's data extraction methods:

### From ROS Bags

```python
from trajectory_container_tools.dataclasses import NavMsgsOdometry


@dataclass
class ProcessedOdometry(NavMsgsOdometry):

    def on_exit_post_init_callback(self):
        """Extract and compute additional metrics from odometry."""
        # Access nested ROS message structure
        pos_x = self.get_dynamic_attribute("pose.pose.position.x")
        pos_y = self.get_dynamic_attribute("pose.pose.position.y")

        # Compute 2D position magnitude
        position_magnitude = np.sqrt(pos_x ** 2 + pos_y ** 2)
        self.set_dynamic_attribute('position_magnitude', position_magnitude)


# Use with rosbag extractor
trajectory = tct.extractor.from_rosbag(
        rosbag_path,
        features_config={"/odom": ProcessedOdometry},
        chunk_on="/odom"
        )
```

### From DataFrames

```python
@dataclass
class BatchTrajectory(tct.BaseTrajectoryFeature):
    x: np.ndarray
    y: np.ndarray

    def on_exit_post_init_callback(self):
        """Handle batch-specific processing."""
        if self.batch:
            # Shape: (batch_size, trajectory_length, ...)
            batch_size = self.x.shape[0]
            self.set_dynamic_attribute("batch_size", batch_size)

            # Compute per-batch statistics
            batch_means = np.mean(self.x, axis=1)
            self.set_dynamic_attribute("batch_x_means", batch_means)


# Use with dataframe extractor
trajectory = tct.extractor.from_dataframe(
        dataframe, features_config={"/trajectory": BatchTrajectory},
        )

```

## Common Patterns

### Pattern 1: Feature Normalization

```python
def post_init_feature_callback(self, feature_name: str):
    """Normalize all numeric features to [0, 1] range."""
    feature = self.get_dynamic_attribute(feature_name)

    if isinstance(feature, np.ndarray) and np.issubdtype(feature.dtype, np.number):
        min_val = np.min(feature)
        max_val = np.max(feature)

        if max_val > min_val:
            normalized = (feature - min_val) / (max_val - min_val)
            self.set_dynamic_attribute(f"{feature_name}_normalized", normalized)
```

### Pattern 2: Temporal Derivatives

```python
def post_init_feature_callback(self, feature_name: str):
    """Compute first and second derivatives for temporal features."""
    feature = self.get_dynamic_attribute(feature_name)

    if isinstance(feature, np.ndarray) and feature_name in ['x', 'y', 'velocity']:
        # First derivative (velocity or acceleration)
        first_deriv = np.diff(feature, prepend=feature[0])
        self.set_dynamic_attribute(f"{feature_name}_dot", first_deriv)

        # Second derivative (acceleration or jerk)
        second_deriv = np.diff(first_deriv, prepend=first_deriv[0])
        self.set_dynamic_attribute(f"{feature_name}_ddot", second_deriv)
```

### Pattern 3: Conditional Processing

```python
def on_exit_post_init_callback(self):
    """Apply different processing based on trajectory characteristics."""
    trajectory_length = len(self.x)

    if trajectory_length < 10:
        # Short trajectory: use simple smoothing
        self.set_dynamic_attribute('processing_mode', 'simple')
    else:
        # Long trajectory: apply advanced filtering
        self.set_dynamic_attribute('processing_mode', 'advanced')

        # Apply moving average
        window = 5
        smoothed_x = np.convolve(self.x, np.ones(window) / window, mode='same')
        self.set_dynamic_attribute('x_smoothed', smoothed_x)
```

## Related Documentation

- [Direct Instantiation Guide](direct_instantiation.md) - Basic usage of trajectory containers
- [ROS Bag Usage Guide](rosbag_usage.md) - Extracting trajectories from ROS bags
- [DataFrame Usage Guide](dataframe_usage.md) - Converting DataFrames to trajectories
- [Core Concepts](README.md#core-concepts) - Understanding TCT architecture

## API Reference

For the complete API documentation of the callback methods, see the source code:
- `AbstractTrajectoryCommon.on_begin_post_init_callback()`
- `AbstractTrajectoryCommon.post_init_feature_callback(feature_name)`
- `AbstractTrajectoryCommon.on_exit_post_init_callback()`

Located in: `src/trajectory_container_tools/dataclasses/core/abstract_trajectory_dataclass_common.py`
