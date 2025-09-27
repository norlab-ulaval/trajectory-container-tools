# TCT Import Improvement Proposal

## Executive Summary

This proposal outlines a comprehensive plan to improve the import structure of Trajectory Container Tools (TCT) to make it as intuitive and easy to use as NumPy. The current import system requires users to know deep module paths and specific class names, creating a steep learning curve. The proposed changes will provide a clean, discoverable API while maintaining backward compatibility.

## Current State Analysis

### Current Import Patterns (Pain Points)

From analysis of notebooks, tests, and documentation, users currently need to import like this:

```python
# Current verbose imports
from trajectory_container_tools.rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag,
    extract_single_feature_from_rosbag,
    check_rosbag_path_and_show_available_topics
)
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import (
    NavMsgsOdometry,
    AckermannMsgsAckermannDriveStamped,
    SensorMsgsImu,
    Tf2MsgsTFMessage
)
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import BaseTrajectoryDataclass
from trajectory_container_tools.utils.factory import trajectory_dataclass_factory
from trajectory_container_tools.utils.temporal_tools.timestamps import TimestampCausalOrderingError
```

### Current Package Structure Issues

1. **Empty `__init__.py` files**: Most submodules have empty `__init__.py` files, providing no discoverability
2. **Deep import paths**: Users must know exact module locations
3. **No namespace organization**: Related functionality scattered across different modules
4. **Poor discoverability**: No guidance on what's available in the package
5. **Inconsistent naming**: Mix of abbreviated and full names

## Proposed Import Structure (NumPy-like)

### Target User Experience

```python
import trajectory_container_tools as tct

# Main functionality - intuitive and discoverable
data = tct.from_rosbag(rosbag_path, features_config)
data = tct.from_dataframe(df, features_config)

# Dataclasses organized by domain
odom_data = tct.dataclasses.NavMsgsOdometry(...)
imu_data = tct.dataclasses.SensorMsgsImu(...)

# ROS-specific functionality
tct.ros.check_topics(rosbag_path)
tct.ros.register_non_native_msgs()

# Utilities organized by purpose
factory_class = tct.factory.create_dataclass(specification)
timestamps = tct.temporal.Timestamps(...)
tct.plot.trajectory(data)

# Alternative short imports (like numpy as np)
import trajectory_container_tools as tct
```

## Detailed Implementation Plan

### 1. Reorganize Main Package `__init__.py`

**File: `src/trajectory_container_tools/__init__.py`**

```python
# coding=utf-8
"""
Trajectory Container Tools (TCT)

A library for managing trajectory-related data with support for:
- ROS bag data extraction
- Pandas DataFrame processing  
- Multiple trajectory dataclass types
- Temporal analysis tools
- Visualization utilities

Quick Start:
    import trajectory_container_tools as tct
    
    # Extract from ROS bag
    data = tct.from_rosbag(rosbag_path, features_config)
    
    # Extract from DataFrame
    data = tct.from_dataframe(df, features_config)
    
    # Access dataclasses
    odom_class = tct.dataclasses.NavMsgsOdometry
    
    # Utilities
    tct.ros.check_topics(rosbag_path)
"""

# Version info
from .version import __version__

# Main API - Top-level convenience functions
from .rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag as from_rosbag,
    extract_single_feature_from_rosbag as extract_rosbag_feature,
    check_rosbag_path_and_show_available_topics as check_rosbag
)

from .dataframe_to_tct import (
    aggregate_multiple_features_from_dataframe as from_dataframe,
    extract_single_feature_from_dataframe as extract_dataframe_feature,
    unpack_dataframe_and_show_topic as check_dataframe
)

# Backward compatibility - keep original names
from .rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag,
    extract_single_feature_from_rosbag,
    check_rosbag_path_and_show_available_topics
)

from .dataframe_to_tct import (
    aggregate_multiple_features_from_dataframe,
    extract_single_feature_from_dataframe,
    unpack_dataframe_and_show_topic
)

# Core abstract classes
from .trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass
)
from .trj_dataclasses.base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass
)

# Submodule imports for namespace organization
from . import dataclasses
from . import ros  
from . import factory
from . import temporal
from . import utils
from . import plot

# Common exceptions
from .utils.temporal_tools.timestamps import TimestampCausalOrderingError

__all__ = [
    # Version
    '__version__',
    
    # Main API functions (new names)
    'from_rosbag',
    'from_dataframe', 
    'extract_rosbag_feature',
    'extract_dataframe_feature',
    'check_rosbag',
    'check_dataframe',
    
    # Backward compatibility (original names)
    'aggregate_multiple_features_from_rosbag',
    'extract_single_feature_from_rosbag',
    'check_rosbag_path_and_show_available_topics',
    'aggregate_multiple_features_from_dataframe',
    'extract_single_feature_from_dataframe',
    'unpack_dataframe_and_show_topic',
    
    # Core classes
    'AbstractTrajectoryDataclass',
    'AbstractMultifeatureDataclass', 
    'BaseTrajectoryDataclass',
    'NestedBaseTrajectoryDataclass',
    
    # Namespaces
    'dataclasses',
    'ros',
    'factory', 
    'temporal',
    'utils',
    'plot',
    
    # Common exceptions
    'TimestampCausalOrderingError',
]
```

### 2. Create Dataclasses Namespace

**File: `src/trajectory_container_tools/trj_dataclasses/__init__.py`**

```python
# coding=utf-8
"""
Trajectory dataclasses for different data sources and formats.

Available dataclasses:
- ROS2 message types (NavMsgsOdometry, SensorMsgsImu, etc.)
- Simulation environments (F110Gym, MathGymnasium, etc.) 
- Generic containers (BaseTrajectoryDataclass, etc.)

Usage:
    import trajectory_container_tools as tct
    odom_class = tct.dataclasses.NavMsgsOdometry
    imu_class = tct.dataclasses.SensorMsgsImu
"""

# Abstract base classes
from .abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass
)

# Base implementations
from .base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass
)

# ROS2 dataclasses
from .ros2_feature_dataclass import (
    NavMsgsOdometry,
    SensorMsgsImu,
    AckermannMsgsAckermannDriveStamped,
    AckermannMsgsAckermannDrive,
    Tf2MsgsTFMessage,
    VescMsgsVescImuStamped,
    Scan,
    RosStampedDataclass,
    RosDataclass,
    NestedRosStampedDataclass
)

from .ros2_primitive_dataclass import Header

# Simulation environment dataclasses  
from .f110_gym_trajectory_dataclass import F110GymTrajectoryDataclass
from .math_gymnasium_trajectory_dataclass import MathGymnasiumTrajectoryDataclass
from .erll_trajectory_dataclass import ErllTrajectoryDataclass

# DataFrame dataclasses
from .panda_dataframe_feature_dataclass import (
    BaseDataframeFeatureDataclass,
    PandaDataframeFeatureDataclass
)

# Primitive types
from .primitive_dataclass import PrimitiveDataclass

__all__ = [
    # Abstract classes
    'AbstractTrajectoryDataclass',
    'AbstractMultifeatureDataclass',
    
    # Base classes
    'BaseTrajectoryDataclass', 
    'NestedBaseTrajectoryDataclass',
    
    # ROS2 dataclasses
    'NavMsgsOdometry',
    'SensorMsgsImu', 
    'AckermannMsgsAckermannDriveStamped',
    'AckermannMsgsAckermannDrive',
    'Tf2MsgsTFMessage',
    'VescMsgsVescImuStamped',
    'Scan',
    'RosStampedDataclass',
    'RosDataclass',
    'NestedRosStampedDataclass',
    'Header',
    
    # Simulation environments
    'F110GymTrajectoryDataclass',
    'MathGymnasiumTrajectoryDataclass', 
    'ErllTrajectoryDataclass',
    
    # DataFrame
    'BaseDataframeFeatureDataclass',
    'PandaDataframeFeatureDataclass',
    
    # Primitives
    'PrimitiveDataclass',
]
```

### 3. Create ROS Namespace

**File: `src/trajectory_container_tools/ros.py`**

```python
# coding=utf-8
"""
ROS-specific utilities and functions.

This module provides ROS-related functionality including:
- Topic inspection
- Message type registration
- ROS bag utilities
- Type store management

Usage:
    import trajectory_container_tools as tct
    tct.ros.check_topics(rosbag_path)
    tct.ros.register_non_native_msgs()
"""

# ROS utilities
from .rosbag_to_tct import check_rosbag_path_and_show_available_topics as check_topics
from .utils.ros2_non_native_msg import register_ros2_non_native_msg as register_non_native_msgs
from .utils.ros2_utils import (
    get_rosbag_typestore_auto_distro,
    rosbag_topic_time_to_timestamp
)

# ROS dataclasses (convenient access)
from .trj_dataclasses.ros2_feature_dataclass import (
    NavMsgsOdometry,
    SensorMsgsImu,
    AckermannMsgsAckermannDriveStamped,
    Tf2MsgsTFMessage,
    VescMsgsVescImuStamped,
    Scan
)

__all__ = [
    # Utilities
    'check_topics',
    'register_non_native_msgs', 
    'get_rosbag_typestore_auto_distro',
    'rosbag_topic_time_to_timestamp',
    
    # Common ROS dataclasses
    'NavMsgsOdometry',
    'SensorMsgsImu',
    'AckermannMsgsAckermannDriveStamped', 
    'Tf2MsgsTFMessage',
    'VescMsgsVescImuStamped',
    'Scan',
]
```

### 4. Create Factory Namespace

**File: `src/trajectory_container_tools/factory.py`**

```python
# coding=utf-8
"""
Factory functions for creating trajectory dataclasses dynamically.

Usage:
    import trajectory_container_tools as tct
    
    spec = tct.factory.TrjDataClassFeatureSpecification(
        new_feature_dataclass_type='CustomType',
        dimension_names=('x', 'y', 'z')
    )
    
    new_class = tct.factory.create_dataclass(spec)
"""

from .utils.factory import (
    trajectory_dataclass_factory as create_dataclass,
    parse_to_feature_dataclass as parse_feature_spec,
    TrjDataClassFeatureSpecification
)

__all__ = [
    'create_dataclass',
    'parse_feature_spec', 
    'TrjDataClassFeatureSpecification',
]
```

### 5. Create Temporal Namespace

**File: `src/trajectory_container_tools/temporal.py`**

```python
# coding=utf-8
"""
Temporal analysis tools for trajectory data.

Includes timestamp handling, sequence ordering, and temporal indexing.

Usage:
    import trajectory_container_tools as tct
    timestamps = tct.temporal.Timestamps(data)
    tct.temporal.validate_ordering(timestamps)
"""

from .utils.temporal_tools.timestamps import (
    Timestamps,
    TimestampCausalOrderingError
)
from .utils.temporal_tools.sequence_ordering import (
    # Add specific functions from this module
)
from .utils.temporal_tools.timestep_indexing import (
    dataframe_timestep_indexing_sanity_check as validate_dataframe_indexing
)

__all__ = [
    'Timestamps',
    'TimestampCausalOrderingError',
    'validate_dataframe_indexing',
]
```

### 6. Create Plot Namespace  

**File: `src/trajectory_container_tools/plot.py`**

```python
# coding=utf-8
"""
Plotting and visualization utilities for trajectory data.

Usage:
    import trajectory_container_tools as tct
    tct.plot.trajectory(data)
"""

from .utils.plot import (
    # Import plotting functions - analyze utils/plot.py for available functions
)

__all__ = [
    # Add plotting function names here
]
```

### 7. Enhanced Utils Namespace

**File: `src/trajectory_container_tools/utils/__init__.py`**

```python
# coding=utf-8
"""
General utilities and helper functions.

Usage:
    import trajectory_container_tools as tct
    tct.utils.general.camelcase_to_snake_case(name)
"""

from .general import (
    camelcase_to_snake_case,
    extract_class_name_from_type,
    setup_progressbar,
    dn_validate_path
)

from .containers_sanity_checks import (
    # Add functions from this module
)

from .optimization import (
    # Add functions from this module  
)

from .shadow_data_container import (
    instanciate_shadow_data_container,
    post_process_shadown_data_container
)

from .typing import (
    TrajectoryDataclass,
    MultifeatureTrajectoryDataclass,
    ShadowDataContainer
)

from .filtered_rosbag_creator import (
    # Add functions from this module
)

__all__ = [
    # General utilities
    'camelcase_to_snake_case',
    'extract_class_name_from_type', 
    'setup_progressbar',
    'dn_validate_path',
    
    # Container utilities
    'instanciate_shadow_data_container',
    'post_process_shadown_data_container',
    
    # Type definitions
    'TrajectoryDataclass',
    'MultifeatureTrajectoryDataclass', 
    'ShadowDataContainer',
]
```

## Migration Strategy

### Phase 1: Additive Changes (Backward Compatible)
1. Populate all `__init__.py` files with exports
2. Add new namespace modules (ros.py, factory.py, etc.)
3. Add convenience functions with new names
4. Keep all existing imports working

### Phase 2: Documentation and Examples
1. Update all documentation to show new import patterns
2. Update notebooks with new examples
3. Add migration guide
4. Show both old and new patterns side by side

### Phase 3: Deprecation Warnings (Optional Future)
1. Add deprecation warnings for old import patterns
2. Provide clear migration messages
3. Timeline for eventual removal (if desired)

## Benefits of This Approach

### For New Users
- **Discoverability**: `import tct` and explore with tab completion
- **Intuitive**: Similar to NumPy's organization
- **Logical grouping**: Related functionality together
- **Less typing**: Shorter, more memorable names

### For Existing Users  
- **Backward compatibility**: All existing code continues to work
- **Gradual migration**: Can adopt new patterns incrementally
- **No breaking changes**: Zero disruption to current workflows

### For Documentation
- **Cleaner examples**: Shorter, more readable code snippets
- **Better organization**: Examples can focus on functionality, not imports
- **Easier teaching**: New users can start with simple imports

## Example Usage Comparison

### Before (Current)
```python
from trajectory_container_tools.rosbag_to_tct import aggregate_multiple_features_from_rosbag
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import NavMsgsOdometry
from trajectory_container_tools.utils.ros2_non_native_msg import register_ros2_non_native_msg

register_ros2_non_native_msg()
data = aggregate_multiple_features_from_rosbag(path, info, config)
```

### After (Proposed)
```python
import trajectory_container_tools as tct

tct.ros.register_non_native_msgs()
data = tct.from_rosbag(path, info, config)
```

## Implementation Priority

1. **High Priority**: Main package `__init__.py` and dataclasses namespace
2. **Medium Priority**: ROS and factory namespaces  
3. **Low Priority**: Temporal, plot, and enhanced utils namespaces

## Conclusion

This proposal transforms TCT from a library requiring deep knowledge of internal structure to one that's as approachable as NumPy. The key principles are:

1. **Discoverability**: Users can explore the API naturally
2. **Logical organization**: Related functionality grouped together
3. **Backward compatibility**: No disruption to existing code
4. **Gradual adoption**: Users can migrate at their own pace
5. **NumPy-like experience**: Familiar patterns for Python users

The result will be a library that's much easier to adopt, teach, and use in practice while maintaining all existing functionality and compatibility.
