# coding=utf-8
"""
Unit tests for the new namespace modules created as part of the TCT import improvement proposal.

These tests verify that the namespace modules (ros.py, factory.py, temporal.py, plot.py) 
properly expose their expected functionality and maintain the correct API structure.
"""

import pytest
import sys
import os

# Add the src directory to path for importing the modules under test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import trajectory_container_tools as tct


class TestRosNamespaceModule:
    """Test the ros.py namespace module functionality."""

    def test_ros_module_exists(self):
        """Test that the ros module exists and can be imported."""
        assert hasattr(tct, 'ros')
        assert tct.ros is not None

    def test_check_topics_function_exists(self):
        """Test that check_topics function is available in ros namespace."""
        assert hasattr(tct.ros, 'check_topics')
        assert callable(tct.ros.check_topics)

    def test_register_non_native_msgs_function_exists(self):
        """Test that register_non_native_msgs function is available in ros namespace."""
        assert hasattr(tct.ros, 'register_non_native_msgs')
        assert callable(tct.ros.register_non_native_msgs)

    def test_get_rosbag_typestore_auto_distro_function_exists(self):
        """Test that get_rosbag_typestore_auto_distro function is available in ros namespace."""
        assert hasattr(tct.ros, 'get_rosbag_typestore_auto_distro')
        assert callable(tct.ros.get_rosbag_typestore_auto_distro)

    def test_rosbag_topic_time_to_timestamp_function_exists(self):
        """Test that rosbag_topic_time_to_timestamp function is available in ros namespace."""
        assert hasattr(tct.ros, 'rosbag_topic_time_to_timestamp')
        assert callable(tct.ros.rosbag_topic_time_to_timestamp)

    def test_ros_dataclasses_available(self):
        """Test that common ROS dataclasses are available in ros namespace."""
        expected_dataclasses = [
            'NavMsgsOdometry',
            'SensorMsgsImu',
            'AckermannMsgsAckermannDriveStamped',
            'Tf2MsgsTFMessage',
            'VescMsgsVescImuStamped',
            'Scan'
        ]
        
        for dataclass_name in expected_dataclasses:
            assert hasattr(tct.ros, dataclass_name), f"Missing dataclass: {dataclass_name}"

    def test_ros_all_attribute(self):
        """Test that ros module has proper __all__ attribute."""
        assert hasattr(tct.ros, '__all__')
        assert isinstance(tct.ros.__all__, list)
        assert len(tct.ros.__all__) > 0


class TestFactoryNamespaceModule:
    """Test the factory.py namespace module functionality."""

    def test_factory_module_exists(self):
        """Test that the factory module exists and can be imported."""
        assert hasattr(tct, 'factory')
        assert tct.factory is not None

    def test_create_dataclass_function_exists(self):
        """Test that create_dataclass function is available in factory namespace."""
        assert hasattr(tct.factory, 'create_dataclass')
        assert callable(tct.factory.create_dataclass)

    def test_parse_feature_spec_function_exists(self):
        """Test that parse_feature_spec function is available in factory namespace."""
        assert hasattr(tct.factory, 'parse_feature_spec')
        assert callable(tct.factory.parse_feature_spec)

    def test_trj_dataclass_feature_specification_exists(self):
        """Test that TrjDataClassFeatureSpecification class is available in factory namespace."""
        assert hasattr(tct.factory, 'TrjDataClassFeatureSpecification')
        assert tct.factory.TrjDataClassFeatureSpecification is not None

    def test_factory_all_attribute(self):
        """Test that factory module has proper __all__ attribute."""
        assert hasattr(tct.factory, '__all__')
        assert isinstance(tct.factory.__all__, list)
        assert len(tct.factory.__all__) > 0


class TestTemporalNamespaceModule:
    """Test the temporal.py namespace module functionality."""

    def test_temporal_module_exists(self):
        """Test that the temporal module exists and can be imported."""
        assert hasattr(tct, 'temporal')
        assert tct.temporal is not None

    def test_timestamps_class_exists(self):
        """Test that Timestamps class is available in temporal namespace."""
        assert hasattr(tct.temporal, 'Timestamps')
        assert tct.temporal.Timestamps is not None

    def test_timestamp_causal_ordering_error_exists(self):
        """Test that TimestampCausalOrderingError is available in temporal namespace."""
        assert hasattr(tct.temporal, 'TimestampCausalOrderingError')
        assert tct.temporal.TimestampCausalOrderingError is not None

    def test_validate_dataframe_indexing_function_exists(self):
        """Test that validate_dataframe_indexing function is available in temporal namespace."""
        assert hasattr(tct.temporal, 'validate_dataframe_indexing')
        assert callable(tct.temporal.validate_dataframe_indexing)

    def test_temporal_all_attribute(self):
        """Test that temporal module has proper __all__ attribute."""
        assert hasattr(tct.temporal, '__all__')
        assert isinstance(tct.temporal.__all__, list)
        assert len(tct.temporal.__all__) > 0


class TestPlotNamespaceModule:
    """Test the plot.py namespace module functionality."""

    def test_plot_module_exists(self):
        """Test that the plot module exists and can be imported."""
        assert hasattr(tct, 'plot')
        assert tct.plot is not None

    def test_trajectory_2d_function_exists(self):
        """Test that trajectory_2d function is available in plot namespace."""
        assert hasattr(tct.plot, 'trajectory_2d')
        assert callable(tct.plot.trajectory_2d)

    def test_plot_all_attribute(self):
        """Test that plot module has proper __all__ attribute."""
        assert hasattr(tct.plot, '__all__')
        assert isinstance(tct.plot.__all__, list)
        assert len(tct.plot.__all__) > 0


class TestMainNamespaceNewAPI:
    """Test the new convenience API functions in the main namespace."""

    def test_from_rosbag_function_exists(self):
        """Test that from_rosbag convenience function is available."""
        assert hasattr(tct, 'from_rosbag')
        assert callable(tct.from_rosbag)

    def test_from_dataframe_function_exists(self):
        """Test that from_dataframe convenience function is available."""
        assert hasattr(tct, 'from_dataframe')
        assert callable(tct.from_dataframe)

    def test_extract_rosbag_feature_function_exists(self):
        """Test that extract_rosbag_feature convenience function is available."""
        assert hasattr(tct, 'extract_rosbag_feature')
        assert callable(tct.extract_rosbag_feature)

    def test_extract_dataframe_feature_function_exists(self):
        """Test that extract_dataframe_feature convenience function is available."""
        assert hasattr(tct, 'extract_dataframe_feature')
        assert callable(tct.extract_dataframe_feature)

    def test_check_rosbag_function_exists(self):
        """Test that check_rosbag convenience function is available."""
        assert hasattr(tct, 'check_rosbag')
        assert callable(tct.check_rosbag)

    def test_check_dataframe_function_exists(self):
        """Test that check_dataframe convenience function is available."""
        assert hasattr(tct, 'check_dataframe')
        assert callable(tct.check_dataframe)


class TestBackwardCompatibility:
    """Test that backward compatibility is maintained for existing API."""

    def test_original_rosbag_functions_exist(self):
        """Test that original rosbag function names are still available."""
        original_functions = [
            'aggregate_multiple_features_from_rosbag',
            'extract_single_feature_from_rosbag',
            'check_rosbag_path_and_show_available_topics'
        ]
        
        for func_name in original_functions:
            assert hasattr(tct, func_name), f"Missing backward compatibility function: {func_name}"
            assert callable(getattr(tct, func_name))

    def test_original_dataframe_functions_exist(self):
        """Test that original dataframe function names are still available."""
        original_functions = [
            'aggregate_multiple_features_from_dataframe',
            'extract_single_feature_from_dataframe',
            'unpack_dataframe_and_show_topic'
        ]
        
        for func_name in original_functions:
            assert hasattr(tct, func_name), f"Missing backward compatibility function: {func_name}"
            assert callable(getattr(tct, func_name))

    def test_core_classes_available(self):
        """Test that core abstract classes are available in main namespace."""
        core_classes = [
            'AbstractTrajectoryDataclass',
            'AbstractMultifeatureDataclass',
            'BaseTrajectoryDataclass',
            'NestedBaseTrajectoryDataclass'
        ]
        
        for class_name in core_classes:
            assert hasattr(tct, class_name), f"Missing core class: {class_name}"

    def test_common_exception_available(self):
        """Test that TimestampCausalOrderingError is available in main namespace."""
        assert hasattr(tct, 'TimestampCausalOrderingError')
        assert tct.TimestampCausalOrderingError is not None


class TestDataclassesNamespace:
    """Test that the dataclasses namespace works correctly."""

    def test_dataclasses_namespace_exists(self):
        """Test that dataclasses namespace exists."""
        assert hasattr(tct, 'dataclasses')
        assert tct.dataclasses is not None

    def test_ros2_dataclasses_available_in_namespace(self):
        """Test that ROS2 dataclasses are available in dataclasses namespace."""
        ros2_dataclasses = [
            'NavMsgsOdometry',
            'SensorMsgsImu',
            'AckermannMsgsAckermannDriveStamped',
            'Tf2MsgsTFMessage',
            'VescMsgsVescImuStamped',
            'Scan'
        ]
        
        for dataclass_name in ros2_dataclasses:
            assert hasattr(tct.dataclasses, dataclass_name), f"Missing dataclass: {dataclass_name}"

    def test_abstract_classes_available_in_namespace(self):
        """Test that abstract classes are available in dataclasses namespace."""
        abstract_classes = [
            'AbstractTrajectoryDataclass',
            'AbstractMultifeatureDataclass',
            'BaseTrajectoryDataclass',
            'NestedBaseTrajectoryDataclass'
        ]
        
        for class_name in abstract_classes:
            assert hasattr(tct.dataclasses, class_name), f"Missing abstract class: {class_name}"


class TestNamespacesConsistency:
    """Test that namespaces are consistent and properly structured."""

    def test_all_namespaces_have_all_attribute(self):
        """Test that all namespace modules have __all__ attribute properly defined."""
        namespaces = ['ros', 'factory', 'temporal', 'plot', 'dataclasses', 'utils']
        
        for namespace_name in namespaces:
            namespace = getattr(tct, namespace_name)
            assert hasattr(namespace, '__all__'), f"Missing __all__ in {namespace_name} namespace"
            assert isinstance(namespace.__all__, list), f"__all__ is not a list in {namespace_name} namespace"
            assert len(namespace.__all__) > 0, f"Empty __all__ in {namespace_name} namespace"

    def test_main_package_all_attribute(self):
        """Test that main package has comprehensive __all__ attribute."""
        assert hasattr(tct, '__all__')
        assert isinstance(tct.__all__, list)
        assert len(tct.__all__) > 0
        
        # Check that key sections are included
        expected_sections = [
            '__version__',
            'from_rosbag',
            'from_dataframe', 
            'dataclasses',
            'ros',
            'factory',
            'temporal',
            'utils',
            'plot'
        ]
        
        for item in expected_sections:
            assert item in tct.__all__, f"Missing item in main __all__: {item}"
