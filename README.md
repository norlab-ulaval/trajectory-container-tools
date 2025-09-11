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
**A library for managing trajectory related data. Provide trajectory dataclasses of various type, factory function, rosbag extractor, pandas dataframe extractor and various utilities.**
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

**Trajectory Container Tools (TCT)** is a Python library designed to simplify the management and analysis of trajectory data from various sources. It provides:

- **Trajectory Dataclasses**: 
  - Type-safety for different trajectory formats (e.g., 2D/3D poses, velocities, commands)
  - Timesteps iterable object over the trajectory horizon
  - Data causality validation i.e., guarantee to have strictly monotonicaly increassing timestamps
- **Data Converters**: Extract trajectory data from pandas DataFrames and ROS bags
- **Factory Functions**: Dynamically create trajectory containers based on configuration
- **Utilities**: Timestamps ordering validation, container timestamp alignment check, plotting, and filtering tools

Whether you're working with robotics research, autonomous systems, or trajectory analysis, TCT provides a unified interface for handling trajectory data across different formats and sources.

## Why

### 🎯 **Unified Data Interface**
- Aggregate data in one trajectory wide iterable object
- Type-safe dataclasses ensure data integrity and provide clear structure
- Work with trajectory data from multiple sources (DataFrames, ROS bags, direct instantiation) using a consistent API

### 🔧 **Flexible & Extensible**  
- Factory pattern allows dynamic creation of trajectory containers
- Easy to extend with custom trajectory types and post-processing callback logic
- Support for both single trajectories and multi-feature datasets

### 🚀 **Research-Ready**
- Built for robotics and AI research workflows
- Integration with common research tools (pandas, matplotlib, ROS2)

### ✅ **Data Validation**
- Automatic sanity checks for trajectory data consistency
- Timestamp validation and monotonicity checks
- Dimension and shape validation

## How Does It Work?

TCT follows a simple three-step process:

### 1. **Data Source** → 2. **Converter** → 3. **Trajectory Container**

#### From direct instantiation 
```python
from trajectory_container_tools.trj_dataclasses.panda_dataframe_feature_dataclass import StatePose2D

trajectory = StatePose2D(feature_name="odom pose",
                         x=np.arange(100, dtype=float),
                         y=np.arange(100, dtype=float),
                         yaw=np.arange(100, dtype=float),
                         timesteps=np.arange(100, dtype=int),
                         )
```
             
#### From ROS bag
```python
from trajectory_container_tools.rosbag_to_tct import aggregate_multiple_features_from_rosbag
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import NavMsgsOdometry,
    AckermannMsgsAckermannDriveStamped

dataset_info = f"Warthog Mont-Morency {datetime.now()}"
features_config = {"/odom": NavMsgsOdometry, "/teleop": AckermannMsgsAckermannDriveStamped}

trajectory = aggregate_multiple_features_from_rosbag(rosbag_path, dataset_info, features_config)

len(trajectory.topic_odom.pose)
# 3120
```

#### From pandas DataFrame
```python
from datetime import datetime
import numpy as np
from trajectory_container_tools.dataframe_to_tct import aggregate_multiple_features_from_dataframe
from trajectory_container_tools.trj_dataclasses.panda_dataframe_feature_dataclass import StatePose2DSteadyState

dataset_info = f"Warthog Mont-Morency {datetime.now()}"
features_config = {'icp_vel': StatePose2DSteadyState, 'idd_vel': StatePose2DSteadyState, }

trajectory = aggregate_multiple_features_from_dataframe(dataframe, dataset_info, features_config)

assert trajectory.idd_vel.x.shape == trajectory.icp_vel.x.shape
# True
```

#### Create your own custom data trajectory container
```python
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import BaseTrajectoryDataclass


class CustomStatePose2D(BaseTrajectoryDataclass)
    x: np.ndarray
    y: np.ndarray
    yaw: np.ndarray

```

## Getting started

### Option 1: Clone and Install with pip

```bash
# Clone the repository
git clone https://github.com/norlab-ulaval/trajectory-container-tools.git
cd trajectory-container-tools

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install trajectory-container-tools
```

### Option 2: Using DNA (Dockerized-NorLab Application)

```bash
# Build and run the container
cd trajectory-container-tools
dna build develop
dna up
```

The DNA approach provides a containerized environment with all dependencies pre-installed, ideal for reproducible research and development.

## Examples

Interactive Jupyter notebook examples:

- **[Dataclass Usage Examples](notebooks/dataclass_usage_example.ipynb)** - Direct trajectory container instantiation
- **[ROS Bag Usage Examples](notebooks/rosbag_usage_example.ipynb)** - Extract trajectory data from ROS bags
- **[DataFrame Usage Examples](notebooks/dataframe_usage_example.ipynb)** - Convert pandas DataFrames to trajectory containers

## Documentation

📚 **[Full Documentation](documentation/README.md)**

- [ROS Bag Usage](documentation/rosbag_usage.md)  
- [Pandas DataFrame Usage](documentation/dataframe_usage.md)
- [Direct Instantiation](documentation/direct_instantiation.md)

[//]: # (## Contributing)

[//]: # ()
[//]: # (We welcome contributions! Please see our [contribution guidelines]&#40;CONTRIBUTING.md&#41; for details.)

[//]: # ()
[//]: # (## License)

[//]: # ()
[//]: # (This project is licensed under the MIT License - see the [LICENSE]&#40;LICENSE&#41; file for details.)


