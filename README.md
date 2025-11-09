<div align="center">

[//]: # ( ==== Logo ================================================== )
<br>
<br>
<a href="https://norlab.ulaval.ca">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="/visual/norlab_logo_acronym_light.png">
      <source media="(prefers-color-scheme: light)" srcset="/visual/norlab_logo_acronym_dark.png">
      <img alt="Shows an the dark NorLab logo in light mode and light NorLab logo in dark mode." src="/visual/norlab_logo_acronym_dark.png" width="175">
    </picture>
</a>
<br>
<br>

[//]: # ( ==== Title ================================================= )

# _Trajectory Container Tools_

[//]: # ( ==== Hyperlink ============================================= )

<sup>
    <a href="https://github.com/norlab-ulaval/dockerized-norlab-project">Dockerized-NorLab project app (DNA)</a>
    &nbsp; • &nbsp;
    <a href="https://hub.docker.com/repositories/norlabulaval">NorLab Docker Hub</a> 
    &nbsp; • &nbsp;
    <a href="http://132.203.26.125:8111">NorLab TeamCity (vpn/intranet)</a> 
</sup>
<br>
<br>

[//]: # ( ==== Description =========================================== )
**A library for managing trajectory related data. Provide trajectory dataclasses of various type, factory function,
rosbag extractor, pandas dataframe extractor and various utilities.**
<br>

[//]: # ( ==== Badges ================================================ )

[//]: # (Note on shield.io release badge: it works only for public repository)

[![semantic-release: conventional commits](https://img.shields.io/badge/semantic--release-conventional_commits-453032?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
<img alt="GitHub release (with filter)" src="https://img.shields.io/github/v/release/norlab-ulaval/trajectory-container-tools?include_prereleases">


[//]: # (NorLab teamcity)

[![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](./reports/coverage/htmlcov/index.html)
<a href="http://132.203.26.125:8111"><img alt="Static Badge" src="https://img.shields.io/badge/JetBrains%20TeamCity-CI-green?style=plastic&logo=teamcity"></a>

[//]: # (Dockerhub image badge)

[//]: # (TODO: Un-comment the next line if you have docker images on dockerhub)

[//]: # (TODO: Change "norlabulaval/libpointmatcher" in both url to "your-dockerhub-domain/your-image-name")

[//]: # (<a href="https://hub.docker.com/repository/docker/norlabulaval/libpointmatcher/"> <img alt="Docker Image Version &#40;latest semver&#41;" src="https://img.shields.io/docker/v/norlabulaval/libpointmatcher?logo=docker"> </a>)


<br>

[//]: # ( ==== Maintainer ============================================ )
<sub>
Maintainer <a href="https://github.com/RedLeader962">RedLeader962</a>
</sub>

<br>
<hr style="color:lightgray;background-color:lightgray">
</div>

[//]: # ( ==== Body ================================================== )

## What it does

**Trajectory Container Tools (TCT)** is a Python library designed to simplify the management and analysis of trajectory
data from various sources.

### High-Level Overview

TCT provides:

- **Trajectory Dataclasses**:
    - Type-safety for different trajectory formats (e.g., 2D/3D poses, velocities, commands)
    - Trajectory wide indexing and slicing
    - Trajectory wide iterable i.e., timesteps iterable from `t=0` to `t=T`
    - Time logical and causal ordering validation i.e., guarantee to have strictly monotonicaly increassing timestep
      indices and timestamps
- **Multi-Feature Containers**:
    - Aggregate multiple trajectory features (e.g., odometry + commands + IMU) in a single container
    - Support for both stamped and non-stamped trajectory dataclasses aggregation
    - Chunk-based iteration over timestamp windows for synchronized multi-feature data access
    - Aggregate timestamps across features with `trajectory_published_timestamps` and `trajectory_timestamps_metadata`
    - Extract data within timestamp ranges using `get_timestamps_interval()`
- **Enhanced Timestamp Utilities**:
    - Timestamp boundary checking
    - Find nearest timestamps (past/future) for data synchronization
    - Robust error handling with `TimestampMissingError` and `TimestampOutOfBoundError`
    - Temporal ordering validation with detailed error reporting
    - Convert between nanoseconds and seconds representation
- **Data Converters**: Extract trajectory data from pandas DataFrames and ROS2 bags
- **Factory Functions**: Dynamically create trajectory containers based on configuration
- **Utilities**: Timestamps ordering validation, container timestamp alignment check, plotting, and filtering tools

Whether you're working with robotics research, autonomous systems, or trajectory analysis, TCT provides a unified
interface for handling trajectory data across different formats and sources.

## Why

### 🎯 **Unified Data Interface**

- Aggregate data in one trajectory wide iterable object
- Type-safe dataclasses ensure data integrity and provide clear structure
- Work with trajectory data from multiple sources (DataFrames, ROS2 bags, direct instantiation) using a consistent API

### 🔧 **Flexible & Extensible**

- Factory pattern allows dynamic creation of trajectory containers
- Straight forward to extend with custom trajectory types and post-processing callback logic
- Support trajectory time-series and batching i.e., array shape `(trj_len, ...)` and `(batch_size, trj_len, ...)`
- Support for both single feature and multi-feature datasets

### 🚀 **Research-Ready**

- Built for robotics and AI research workflows
- Integration with common research tools (pandas, matplotlib, numpy, ROS2)
- Reliable → TCT as decent codecoverage and is periodicaly tested in CI

### ✅ **Data Validation**

- Automatic sanity checks for trajectory data consistency
- Timestamp validation
- Dimension and shape validation

## Getting started

### For user

#### Optiona 1: pip install from repository
```bash
# Minimal install
pip install git+https://github.com/norlab-ulaval/trajectory-container-tools.git

# Full install with ros support 
pip install "git+https://github.com/norlab-ulaval/trajectory-container-tools.git#egg=trajectory-container-tools[ros]"
```

#### Optiona 2: install from PyPI (when available) 
```bash
# Minimal install
pip install trajectory-container-tools

# Full install with ros support 
pip install trajectory-container-tools[ros]
```

The `ros` install extra enable two specialized namespaces i.e., `extractor` and `ros` which provide functionalities for extracting data from rosbag and from dataframe as well as functionalities directly related to rosbag handling and ros time. 

### For developer, playing with the interactive example Jupyter notebook or using the `tests_data` 

#### Option 1: Clone and Install with pip

```bash
# Clone the repository
git clone https://github.com/norlab-ulaval/trajectory-container-tools.git
cd trajectory-container-tools

# Install in development mode
pip install -e .[ros,dev]
```

The `dev` install extra install developement dependencies.

#### Option 2: Using DNA ([Dockerized-NorLab Application](https://github.com/norlab-ulaval/dockerized-norlab-project))

```bash
# Build and run the container
cd trajectory-container-tools
dna build develop
dna up
```

The DNA approach provides a containerized environment with all dependencies pre-installed including Jupyter server, 
ideal for reproducible research and development.


## How Does It Work?

Begin by importing the _Trajectory Container Tools_ namespace 
```python
import trajectory_container_tools as tct
```

Then, it's a three-step process: 1. **Data Source** → 2. **Instanciate Trajectory Container** → 3. **Use it**

Common use cases:

- **From direct instantiation** i.e., manualy instanciating trajectory dataclasses.
- **From ROS bag** using rosbag to trajectory dataclasses extractor.
- **From pandas DataFrame** using dataframe to trajectory dataclasses extractor.

### From direct instantiation

#### Use one of the many predifined trajectory dataclass from the `tct.dataclasses` module 

```python
import trajectory_container_tools as tct
import numpy as np

# Example using a 2D pose primitive trajectory dataclass
trajectory = tct.dataclasses.Pose2DSA(
        feature_name="2D pose example",
        x=np.arange(100, dtype=float),
        y=np.arange(100, dtype=float),
        theta=np.linspace(start=0, stop=360, num=100, dtype=np.float16),
        )

print(trajectory)
```

```text
Pose2DSA(
   feature_name: "2D pose example"
   trajectory_len: 100
   transposed: False
   x: (ndarray) shape (100,) range 0.0 ←→ 99.0
   y: (ndarray) shape (100,) range 0.0 ←→ 99.0
   theta: (ndarray) shape (100,) range 0.0 ←→ 360.0
)
```

#### Define your own custom data trajectory container

```python
import numpy as np
import trajectory_container_tools as tct


class CustomStatePose2D(tct.BaseTrajectoryFeature):
  x: np.ndarray
  y: np.ndarray
  yaw: np.ndarray
```


#### Trajectory containers are trajectory wide iterable object which support indexing and slicing

```python
# Example accessing interval t=10 to t=15
print(trajectory[10:15])
```

```text
Pose2DSA(
   feature_name: "2D pose example"
   trajectory_len: 5
   transposed: False
   x: (ndarray) shape (5,) range 10.0 ←→ 14.0
   y: (ndarray) shape (5,) range 10.0 ←→ 14.0
   theta: (ndarray) shape (5,) range 36.375 ←→ 50.90625
)    
```

```python
# Example accessing the last theta value
print(trajectory[-1].theta)
# 360
```

#### Post-Processing with Callbacks

TCT provides three callback methods for custom data post-processing during instantiation:

```python
import numpy as np
from dataclasses import dataclass
import trajectory_container_tools as tct


@dataclass
class CustomTrajectoryWithCallbacks(tct.BaseTrajectoryFeature):
  x: np.ndarray
  y: np.ndarray
  velocity: np.ndarray
  
  def on_begin_post_init_callback(self):
    """Executed at the beginning of __post_init__, before feature processing.
    Use for initialization logic that affects all fields."""
    # Example: Ensure data is in correct format
    if self.x.dtype != np.float64:
      self.set_dynamic_attribute('x', self.x.astype(np.float64))
  
  def post_init_feature_callback(self, feature_name: str):
    """Executed once per feature (excluding internal/non-trajectory fields).
    Use for feature-specific post-processing."""
    # Example: Create cumulative sum features
    feature = self.get_dynamic_attribute(feature_name)
    if isinstance(feature, np.ndarray) and feature_name in ['x', 'y']:
      cumsum = np.cumsum(feature)
      self.set_dynamic_attribute(f"{feature_name}_cumsum", cumsum)
  
  def on_exit_post_init_callback(self):
    """Executed at the end of __post_init__, after all processing.
    Use for final validation or computed properties."""
    # Example: Compute total distance traveled
    dx = np.diff(self.x, prepend=0)
    dy = np.diff(self.y, prepend=0)
    distance = np.sqrt(dx ** 2 + dy ** 2)
    self.set_dynamic_attribute('distance', distance)


# Instantiate with automatic callback execution
trajectory = CustomTrajectoryWithCallbacks(
        feature_name="Callback example",
        x=np.arange(10, dtype=float),
        y=np.arange(10, dtype=float),
        velocity=np.random.rand(10),
        )

# Access dynamically created fields
print(f"X cumsum: {trajectory.x_cumsum}")
print(f"Total distance: {trajectory.distance.sum():.2f}")
```
```text
X cumsum: [ 0.  1.  3.  6. 10. 15. 21. 28. 36. 45.]
Total distance: 12.73
```

**Callback Execution Order:**
1. `on_begin_post_init_callback()` - Once at start
2. `post_init_feature_callback(feature_name)` - Once per feature
3. `on_exit_post_init_callback()` - Once at end

For more details, see the [Post-Processing Callbacks documentation](documentation/post_processing_callbacks.md).

### Typing and Internal Fields

TCT introduces typing markers to control how fields are treated by the container logic:
- `tct.typing.NonTrajectoryField[T]` marks a field that is not per‑timestep (e.g., metadata arrays, labels).
  Such fields are excluded from iteration, transpose `T`, and ravel operations.
- `tct.typing.ContainerInternalField[T]` marks an internal field used by the container implementation. These fields are not exposed by `get_public_attribute_names()` and are ignored by feature processing callbacks.

Example:

```python
from dataclasses import dataclass, field
import numpy as np
import trajectory_container_tools as tct


@dataclass
class TrajectoryWithMeta(tct.BaseTrajectoryFeature):
  x: np.ndarray
  y: np.ndarray
  timestamps: np.ndarray
  # Non‑trajectory: excluded from per‑timestep logic
  metadata: tct.typing.NonTrajectoryField[np.ndarray] = field(default_factory=lambda: np.array([1, 2, 3]))
  # Internal: not exposed to users, can be set programmatically
  _timestep_indexes: tct.typing.ContainerInternalField[np.ndarray] = field(default=None, init=False)


traj = TrajectoryWithMeta(feature_name="demo", x=np.arange(5), y=np.arange(5), timestamps=np.arange(5))
print(traj.get_public_attribute_names())  # ('x','y','timestamps','metadata') — '_timestep_indexes' is hidden

# Dynamic attribute utilities
traj.set_dynamic_attribute('x_cumsum', np.cumsum(traj.x))
print(traj.get_dynamic_attribute('x_cumsum'))
print(traj.has_dynamic_attribute('x_cumsum'))  # True
```

See the detailed guide: documentation/typing_and_internal_fields.md

### From ROS bag

```python
import trajectory_container_tools as tct

trajectory_from_rosbag = tct.extractor.from_rosbag(
    rosbag_path,
    dataset_info="Warthog Mont-Morency 1 Dec 2025",
    features_config={
        "/odom": tct.dataclasses.NavMsgsOdometry,
        "/teleop": tct.dataclasses.AckermannMsgsAckermannDriveStamped,
    },
    chunk_on="/teleop",
)

print(trajectory_from_rosbag)

```

```text
Fetch rosbag typestore for ros2 humble
[TCT] Extract single feature from rosbag › seeking /odom
[TCT] Collect topic /odom msg from rosbag
       ↳ 100%|██████████| 864/864
[TCT] Post-process rosbag data and configure NavMsgsOdometry container
       ↳ 100%|██████████| 5/5
[TCT] Extract single feature from rosbag › seeking /teleop
[TCT] Collect topic /teleop msg from rosbag
       ↳ 100%|██████████| 783/783
[TCT] Post-process rosbag data and configure AckermannMsgsAckermannDriveStamped container
       ↳ 100%|██████████| 4/4

TrajectoryFeaturesBag(
   dataset_info: Warthog Mont-Morency 1 Dec 2025
   aggregated_date: 2025-10-21 23:52:43.807338
   chunks_total: 783
   bag_timestamps:       
       Timestamps(
          stamps: shape (1647,) range 1695601812731601521 ←→ 1695601829992486976 (nanosec)
          delta_stamps: shape (1647,) range 57123 ←→ 31644756 (nanosec)
       )
   chunk_on: topic_teleop
   topic_odom:      
      NavMsgsOdometry(
         feature_name: "/odom"
         bag_recorded_timestamps:      
            Timestamps(
               stamps: shape (864,) range 1695601812734067638 ←→ 1695601829992486976 (nanosec)
               delta_stamps: shape (864,) range 6953885 ←→ 32941128 (nanosec)
            )
         header:      
            StdMsgsHeader(
               frame_id: (str) odom
               timestamps:      
                  Timestamps(
                     stamps: shape (864,) range 1695601812731516173 ←→ 1695601829991973387 (nanosec)
                     delta_stamps: shape (864,) range 14921477 ←→ 24975650 (nanosec)
                  )
            )
         pose:      
            GeometryMsgsPoseWithCovariance(
               pose:      
                  GeometryMsgsPose(
                     position:      
                        GeometryMsgsPoint(
                           x: (ndarray) shape (864,) range -1.7077189281656129 ←→ 2.135440133972323
                           y: (ndarray) shape (864,) range -1.8602605361391937 ←→ 1.84745732132406
                           z: (ndarray) shape (864,) range 0.0 ←→ 0.0
                        )
                     orientation:      
                        GeometryMsgsQuaternion(
                           x: (ndarray) shape (864,) range 0.0 ←→ 0.0
                           y: (ndarray) shape (864,) range 0.0 ←→ 0.0
                           z: (ndarray) shape (864,) range -0.9999998984079552 ←→ 0.7856382323820762
                           w: (ndarray) shape (864,) range -0.999999584403138 ←→ 0.8295177267380831
                        )
                  )
               covariance: (ndarray) shape (864, 36) range 0.0 ←→ 0.4
            )
         twist:      
            GeometryMsgsTwistWithCovariance(
               twist:      
                  GeometryMsgsTwist(
                     linear:      
                        GeometryMsgsVector3(
                           x: (ndarray) shape (864,) range 0.0 ←→ 1.578
                           y: (ndarray) shape (864,) range 0.0 ←→ 0.0
                           z: (ndarray) shape (864,) range 0.0 ←→ 0.0
                        )
                     angular:      
                        GeometryMsgsVector3(
                           x: (ndarray) shape (864,) range 0.0 ←→ 0.0
                           y: (ndarray) shape (864,) range 0.0 ←→ 0.0
                           z: (ndarray) shape (864,) range -2.0234378278138845 ←→ 1.4445453875396634
                        )
                  )
               covariance: (ndarray) shape (864, 36) range 0.0 ←→ 0.0
            )
      )
   topic_teleop:      
      AckermannMsgsAckermannDriveStamped(
         feature_name: "/teleop"
         bag_recorded_timestamps:      
            Timestamps(
               stamps: shape (783,) range 1695601812731601521 ←→ 1695601829989011954 (nanosec)
               delta_stamps: shape (783,) range 419953 ←→ 172146558 (nanosec)
            )
         header:      
            StdMsgsHeader(
               frame_id: (str) 
               timestamps:      
                  Timestamps(
                     stamps: shape (783,) range 1695601812730780687 ←→ 1695601829988774760 (nanosec)
                     delta_stamps: shape (783,) range 499509 ←→ 172056987 (nanosec)
                  )
            )
         drive:      
            AckermannMsgsAckermannDrive(
               steeringAngle: (ndarray) shape (783,) range -0.4399999976158142 ←→ 0.4399999976158142
               steeringAngleVelocity: (ndarray) shape (783,) range 0.0 ←→ 0.0
               speed: (ndarray) shape (783,) range 0.0 ←→ 1.5618410110473633
               acceleration: (ndarray) shape (783,) range 0.0 ←→ 0.0
               jerk: (ndarray) shape (783,) range 0.0 ←→ 0.0
            )
      )
)
```


### Chunk-based Iteration with AbstractTrajectoryStampedFeaturesBag

When extracting data from ROS bags, you can iterate over synchronized timestamp chunks across multiple features:

```python
import trajectory_container_tools as tct

# Extract features from ROS bag (returns AbstractTrajectoryStampedFeaturesBag)
trajectory_features_bag = tct.extractor.from_rosbag(
        rosbag_path,
        features_config={
                "/odom": tct.dataclasses.NavMsgsOdometry,
                "/cmd":  tct.dataclasses.AckermannMsgsAckermannDriveStamped,
                },
        chunk_on="/cmd",
        )

# Iterate over timestamp chunks
for chunk_idx, chunk in enumerate(trajectory_features_bag):
  print(f"Chunk {chunk_idx}:")
  print(f"  Odometry data: {chunk.topic_odom}")
  print(f"  Command data: {chunk.topic_cmd}")

# Access specific chunk by index
first_chunk = trajectory_features_bag[0]
last_chunk = trajectory_features_bag[-1]

# Get total number of chunks
total_chunks = trajectory_features_bag.chunks_total
print(f"Total chunks: {total_chunks}")
```

This enables processing synchronized multi-sensor data in manageable time windows, particularly useful for:
- (Reinforcement Learnind) Processing ros data while preserving causal relationship between observation and action
- Synchronizing data across multiple sensors/topics
- Time-windowed analysis and feature extraction
- Processing large ROS bags incrementally

### From pandas DataFrame

```python
import trajectory_container_tools as tct

trajectory_from_dataframe = tct.extractor.from_dataframe(
    mock_dataset_snow,
    dataset_info="Marmote Mont-Morency 1 Dec 2025",
    features_config={
        "icp_vel": tct.dataclasses.StatePose2D,
        "idd_vel": tct.dataclasses.StatePose2D,
    },
)

print(trajectory_from_dataframe)

```

```text
TrajectoryFeaturesBag(
   dataset_info: Marmote Mont-Morency 1 Dec 2025
   aggregated_date: 2025-10-10 23:58:10.859334
   icp_vel:      
      StatePose2D(
         feature_name: "icp_vel"
         trajectory_len: 40
         batch: True
         transposed: False
         x: (ndarray) shape (309, 40) range -2.592808355332108 ←→ 2.2912484904743624
         y: (ndarray) shape (309, 40) range -1.1001163567627252 ←→ 2.1924347573561866
         yaw: (ndarray) shape (309, 40) range -5.1769010506208675 ←→ 5.4285684489000285
      )
   idd_vel:      
      StatePose2D(
         feature_name: "idd_vel"
         trajectory_len: 40
         batch: True
         transposed: False
         x: (ndarray) shape (309, 40) range -1.2428955645039088 ←→ 1.1297213512973234
         y: (ndarray) shape (309, 40) range 0.0 ←→ 0.0
         yaw: (ndarray) shape (309, 40) range -2.778633612843154 ←→ 2.8262693649539012
      )
)
```


## Documentation

- [Overview and Core concept](documentation/README.md)
    - ↳ [Direct Instantiation](documentation/direct_instantiation.md)
    - ↳ [Post-Processing Callbacks](documentation/post_processing_callbacks.md)
    - ↳ [ROS Bag Usage](documentation/rosbag_usage.md)
    - ↳ [Pandas DataFrame Usage](documentation/dataframe_usage.md)
    - ↳ [Timestamp Utilities](documentation/timestamp_utilities.md)
- Interactive Jupyter notebook examples:
    - **[Direct Instanciation Usage Examples](notebooks/direct_instanciation_usage_example.ipynb)** - Direct trajectory
      container instantiation
    - **[ROS Bag Usage Examples](notebooks/rosbag_usage_example.ipynb)** - Extract trajectory data from ROS bags
    - **[DataFrame Usage Examples](notebooks/dataframe_usage_example.ipynb)** - Convert pandas DataFrames to trajectory
      containers




