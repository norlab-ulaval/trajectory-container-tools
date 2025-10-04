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

[//]: # (TODO: Un-comment the next line if your repository has run configuration enable on the norlab-teamcity-server)

[//]: # (<a href="http://132.203.26.125:8111"><img alt="Static Badge" src="https://img.shields.io/badge/JetBrains%20TeamCity-CI-green?style=plastic&logo=teamcity"></a>)

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

## How Does It Work?

### Three-step process: 1. **Data Source** → 2. **Instanciate Trajectory Container** → 3. **Use it**

Common use cases:

- From direct instantiation
- From ROS bag
- From pandas DataFrame

#### From direct instantiation

```python
import numpy as np
import trajectory_container_tools as tct
from trajectory_container_tools.dataclasses import StatePose2D

trajectory = StatePose2D(
        feature_name="odom pose",
        x=np.arange(100, dtype=float),
        y=np.arange(100, dtype=float),
        yaw=np.linspace(start=0, stop=360, num=100, dtype=np.float16),
        timesteps_indices=np.arange(100, dtype=int),
        )

print(trajectory)

```

```text
          StatePose2D(
             feature_name: odom pose
             trajectory_len: 100
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (100,) range 0 ←→ 99
                x: (ndarray) shape (100,) range 0.0 ←→ 99.0
                y: (ndarray) shape (100,) range 0.0 ←→ 99.0
                yaw: (ndarray) shape (100,) range 0.0 ←→ 360.0
          )
```

##### Trajectory containers are trajectory wide iterable object which support indexing and slicing

```python
# Trajectory timesteps interval t=10 to t=15
print(trajectory[10:15])
```

```text
          StatePose2D(
             feature_name: odom pose
             trajectory_len: 5
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (5,) range 10 ←→ 14
                x: (ndarray) shape (5,) range 10.0 ←→ 14.0
                y: (ndarray) shape (5,) range 10.0 ←→ 14.0
                yaw: (ndarray) shape (5,) range 36.375 ←→ 50.90625
          )       
```

```python
# Access last yaw value
print(trajectory[-1].yaw)
# 360
```

##### Define your own custom data trajectory container

```python
import numpy as np
import trajectory_container_tools as tct

class CustomStatePose2D(tct.BaseTrajectoryDataclass):
    x: np.ndarray
    y: np.ndarray
    yaw: np.ndarray

```

#### From ROS bag

```python
import trajectory_container_tools as tct
from trajectory_container_tools.dataclasses import NavMsgsOdometry, AckermannMsgsAckermannDriveStamped

trajectory_from_rosbag = tct.extractor.from_rosbag(
        rosbag_path,
        dataset_info="Warthog Mont-Morency 1 Dec 2025",
        features_config={
                "/odom":   NavMsgsOdometry,
                "/teleop": AckermannMsgsAckermannDriveStamped,
                },
        )

print(trajectory_from_rosbag)

```

```text
Fetch rosbag typestore for ros2 humble
[TCT] Extract single feature from rosbag › seeking /odom
[TCT] Collect topic /odom msg from rosbag
       ↳ 100%|██████████| 864/864
[TCT] Post-process rosbag data and configure NavMsgsOdometry container
       ↳ 100%|██████████| 4/4
[TCT] Extract single feature from rosbag › seeking /teleop
[TCT] Collect topic /teleop msg from rosbag
       ↳ 100%|██████████| 783/783
[TCT] Post-process rosbag data and configure AckermannMsgsAckermannDriveStamped container
       ↳ 100%|██████████| 3/3

Multifeature(
   dataset_info: Warthog Mont-Morency 1 Dec 2025
   aggregated_date: 2025-10-04 16:41:39.432044
   bag_timestamps: (Timestamps) shape (1647,) range(nanosec) 1695601812731601521 ←→ 1695601829992486976
   topic_odom: 
          NavMsgsOdometry(
             feature_name: /odom
             trajectory_len: 864
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (864,) range 0 ←→ 863
                header:          
                    Header(
                          frame_id: (str) odom
                          timestamps:                          
                                    Timestamps(
                                          stamps: shape (864,) range 1695601812731516173 ←→ 1695601829991973387 (nanosec)
                                          delta_stamps: shape (864,) range 14921477 ←→ 24975650 (nanosec)
                                    )
                    )
                pose:          
                    PoseWithCovariance(
                          pose:          
                              Pose(
                                    position:          
                                        Point(
                                              x: (ndarray) shape (864,) range -1.7077189281656129 ←→ 2.135440133972323
                                              y: (ndarray) shape (864,) range -1.8602605361391937 ←→ 1.84745732132406
                                              z: (ndarray) shape (864,) range 0.0 ←→ 0.0
                                        )
                                    orientation:          
                                        Quaternion(
                                              x: (ndarray) shape (864,) range 0.0 ←→ 0.0
                                              y: (ndarray) shape (864,) range 0.0 ←→ 0.0
                                              z: (ndarray) shape (864,) range -0.9999998984079552 ←→ 0.7856382323820762
                                              w: (ndarray) shape (864,) range -0.999999584403138 ←→ 0.8295177267380831
                                        )
                              )
                          covariance: (ndarray) shape (864, 36) range 0.0 ←→ 0.4
                    )
                twist:          
                    TwistWithCovariance(
                          twist:          
                              Twist(
                                    linear:          
                                        Vector3(
                                              x: (ndarray) shape (864,) range 0.0 ←→ 1.578
                                              y: (ndarray) shape (864,) range 0.0 ←→ 0.0
                                              z: (ndarray) shape (864,) range 0.0 ←→ 0.0
                                        )
                                    angular:          
                                        Vector3(
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
             feature_name: /teleop
             trajectory_len: 783
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (783,) range 0 ←→ 782
                header:          
                    Header(
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

#### From pandas DataFrame

```python
import trajectory_container_tools as tct
from trajectory_container_tools.dataclasses import StatePose2D

trajectory_from_dataframe = tct.extractor.from_dataframe(
    mock_dataset_snow,
    dataset_info="Marmote Mont-Morency 1 Dec 2025",
    features_config={
        "icp_vel": StatePose2D,
        "idd_vel": StatePose2D,
    },
)

print(trajectory_from_dataframe)

```

```text
Multifeature(
   dataset_info: Marmote Mont-Morency 1 Dec 2025
   aggregated_date: 2025-09-15 15:44:30.815538
   icp_vel: 
          StatePose2D(
             feature_name: icp_vel
             trajectory_len: 40
             batch: True
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (40,) range 0 ←→ 39
                x: (ndarray) shape (309, 40) range -2.592808355332108 ←→ 2.2912484904743624
                y: (ndarray) shape (309, 40) range -1.1001163567627252 ←→ 2.1924347573561866
                yaw: (ndarray) shape (309, 40) range -5.1769010506208675 ←→ 5.4285684489000285
          )
   idd_vel: 
          StatePose2D(
             feature_name: idd_vel
             trajectory_len: 40
             batch: True
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (40,) range 0 ←→ 39
                x: (ndarray) shape (309, 40) range -1.2428955645039088 ←→ 1.1297213512973234
                y: (ndarray) shape (309, 40) range 0.0 ←→ 0.0
                yaw: (ndarray) shape (309, 40) range -2.778633612843154 ←→ 2.8262693649539012
          )
   )
```

## Getting started

### For user

#### Optiona 1: pip install from repository
```bash
pip install git+https://github.com/norlab-ulaval/trajectory-container-tools.git
```

#### Optiona 2: install from PyPI (when available) 
```bash
pip install trajectory-container-tools
```

### For developer, playing with the interactive example Jupyter notebook or using the `tests_data` 

#### Option 1: Clone and Install with pip

```bash
# Clone the repository
git clone https://github.com/norlab-ulaval/trajectory-container-tools.git
cd trajectory-container-tools

# Install in development mode
pip install -e .
```

#### Option 2: Using DNA (Dockerized-NorLab Application)

```bash
# Build and run the container
cd trajectory-container-tools
dna build develop
dna up
```

The DNA approach provides a containerized environment with all dependencies pre-installed, ideal for reproducible
research and development.

## Documentation

- [Overview and Core concept](documentation/README.md)
    - ↳ [Direct Instantiation](documentation/direct_instantiation.md)
    - ↳ [ROS Bag Usage](documentation/rosbag_usage.md)
    - ↳ [Pandas DataFrame Usage](documentation/dataframe_usage.md)
- Interactive Jupyter notebook examples:
    - **[Direct Instanciation Usage Examples](notebooks/direct_instanciation_usage_example.ipynb)** - Direct trajectory
      container instantiation
    - **[ROS Bag Usage Examples](notebooks/rosbag_usage_example.ipynb)** - Extract trajectory data from ROS bags
    - **[DataFrame Usage Examples](notebooks/dataframe_usage_example.ipynb)** - Convert pandas DataFrames to trajectory
      containers




