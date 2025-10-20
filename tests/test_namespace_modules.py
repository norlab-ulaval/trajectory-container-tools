# coding=utf-8
"""
These tests verify that the namespace modules (ros.py, factory.py, temporal.py)
properly expose their expected functionality and maintain the correct API structure.
"""
import pytest


@pytest.fixture(scope="function")
def setup_namespace():
    import trajectory_container_tools as tct

    return tct


class TestRosNamespaceModule:
    """Test the ros.py namespace module functionality."""

    def test_ros_module_exists(self, setup_namespace):
        """Test that the ros module exists and can be imported."""
        tct = setup_namespace
        assert hasattr(tct, "ros")
        assert tct.ros is not None

    def test_create_filtered_rosbag_function_exists(self, setup_namespace):
        """Test that create_filtered_rosbag function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "create_filtered_rosbag")
        assert callable(tct.ros.create_filtered_rosbag)

    def test_run_rosbag_timestamp_eda_function_exists(self, setup_namespace):
        """Test that run_rosbag_timestamp_eda function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "run_rosbag_timestamp_eda")
        assert callable(tct.ros.run_rosbag_timestamp_eda)

    def test_register_non_native_msgs_function_exists(self, setup_namespace):
        """Test that register_non_native_msgs function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "register_non_native_msgs")
        assert callable(tct.ros.register_non_native_msgs)

    def test_check_bag_topics_function_exists(self, setup_namespace):
        """Test that check_bag_topics function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "check_bag_topics")
        assert callable(tct.ros.check_bag_topics)

    def test_get_ros2_distro_function_exists(self, setup_namespace):
        """Test that get_ros2_distro function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "get_ros2_distro")
        assert callable(tct.ros.get_ros2_distro)

    def test_get_rosbag_typestore_auto_distro_function_exists(self, setup_namespace):
        """Test that get_rosbag_typestore_auto_distro function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "get_rosbag_typestore_auto_distro")
        assert callable(tct.ros.get_rosbag_typestore_auto_distro)

    def test_rosbag_topic_time_to_timestamp_function_exists(self, setup_namespace):
        """Test that rosbag_topic_time_to_timestamp function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "rosbag_topic_time_to_timestamp")
        assert callable(tct.ros.rosbag_topic_time_to_timestamp)

    def test_convert_timestamp_from_rosbag_message_function_exists(
        self, setup_namespace
    ):
        """Test that convert_timestamp_from_rosbag_message function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "convert_timestamp_from_rosbag_message")
        assert callable(tct.ros.convert_timestamp_from_rosbag_message)

    def test_rosbag_timestamp_to_ros_time_function_exists(self, setup_namespace):
        """Test that rosbag_timestamp_to_ros_time function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "rosbag_timestamp_to_ros_time")
        assert callable(tct.ros.rosbag_timestamp_to_ros_time)

    def test_rosbag_topic_time_to_ros_time_function_exists(self, setup_namespace):
        """Test that rosbag_topic_time_to_ros_time function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "rosbag_topic_time_to_ros_time")
        assert callable(tct.ros.rosbag_topic_time_to_ros_time)

    def test_gather_rosbag_informations_function_exists(self, setup_namespace):
        """Test that gather_rosbag_informations function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "gather_rosbag_informations")
        assert callable(tct.ros.gather_rosbag_informations)

    def test_gather_rosbag_trajectory_window_informations_function_exists(self, setup_namespace):
        """Test that gather_rosbag_trajectory_window_informations function is available in ros namespace."""
        tct = setup_namespace
        assert hasattr(tct.ros, "gather_rosbag_trajectory_window_informations")
        assert callable(tct.ros.gather_rosbag_trajectory_window_informations)

    def test_ros_all_attribute(self, setup_namespace):
        """Test that ros module has proper __all__ attribute."""
        tct = setup_namespace
        assert hasattr(tct.ros, "__all__")
        assert isinstance(tct.ros.__all__, list)
        assert len(tct.ros.__all__) > 0


class TestFactoryNamespaceModule:
    """Test the factory.py namespace module functionality."""

    def test_factory_module_exists(self, setup_namespace):
        """Test that the factory module exists and can be imported."""
        tct = setup_namespace
        assert hasattr(tct, "factory")
        assert tct.factory is not None

    def test_create_dataclass_function_exists(self, setup_namespace):
        """Test that create_dataclass function is available in factory namespace."""
        tct = setup_namespace
        assert hasattr(tct.factory, "create_dataclass")
        assert callable(tct.factory.create_dataclass)

    def test_parse_feature_spec_function_exists(self, setup_namespace):
        """Test that parse_feature_spec function is available in factory namespace."""
        tct = setup_namespace
        assert hasattr(tct.factory, "parse_feature_spec")
        assert callable(tct.factory.parse_feature_spec)

    def test_trj_dataclass_feature_specification_exists(self, setup_namespace):
        """Test that TrjDataClassFeatureSpecification class is available in factory namespace."""
        tct = setup_namespace
        assert hasattr(tct.factory, "TrjDataClassFeatureSpecification")
        assert tct.factory.TrjDataClassFeatureSpecification is not None

    def test_factory_all_attribute(self, setup_namespace):
        """Test that factory module has proper __all__ attribute."""
        tct = setup_namespace
        assert hasattr(tct.factory, "__all__")
        assert isinstance(tct.factory.__all__, list)
        assert len(tct.factory.__all__) > 0


class TestTemporalNamespaceModule:
    """Test the temporal.py namespace module functionality."""

    def test_temporal_module_exists(self, setup_namespace):
        """Test that the temporal module exists and can be imported."""
        tct = setup_namespace
        assert hasattr(tct, "temporal")
        assert tct.temporal is not None

    def test_timestamps_class_exists(self, setup_namespace):
        """Test that Timestamps class is available in temporal namespace."""
        tct = setup_namespace
        assert hasattr(tct.temporal, "Timestamps")
        assert tct.temporal.Timestamps is not None

    def test_timestamp_causal_ordering_error_exists(self, setup_namespace):
        """Test that TimestampCausalOrderingError is available in temporal namespace."""
        tct = setup_namespace
        assert hasattr(tct.temporal, "TimestampCausalOrderingError")
        assert tct.temporal.TimestampCausalOrderingError is not None

    def test_validate_dataframe_indexing_function_exists(self, setup_namespace):
        """Test that validate_dataframe_timesteps_indexing function is available in temporal namespace."""
        tct = setup_namespace
        assert hasattr(tct.temporal, "validate_dataframe_timesteps_indexing")
        assert callable(tct.temporal.validate_dataframe_timesteps_indexing)

    def test_temporal_all_attribute(self, setup_namespace):
        """Test that temporal module has proper __all__ attribute."""
        tct = setup_namespace
        assert hasattr(tct.temporal, "__all__")
        assert isinstance(tct.temporal.__all__, list)
        assert len(tct.temporal.__all__) > 0


class TestExtractorNamespaceModule:
    """Test the extractor namespace module."""

    def test_extractor_module_exists(self, setup_namespace):
        """Test that extractor namespace exists."""
        tct = setup_namespace
        assert hasattr(tct, "extractor")
        assert tct.extractor is not None

    def test_from_rosbag_function_exists(self, setup_namespace):
        """Test that from_rosbag function is available in extractor namespace."""
        tct = setup_namespace
        assert hasattr(tct.extractor, "from_rosbag")
        assert callable(tct.extractor.from_rosbag)

    def test_from_dataframe_function_exists(self, setup_namespace):
        """Test that from_dataframe function is available in extractor namespace."""
        tct = setup_namespace
        assert hasattr(tct.extractor, "from_dataframe")
        assert callable(tct.extractor.from_dataframe)

    def test_extract_rosbag_feature_function_exists(self, setup_namespace):
        """Test that extract_rosbag_feature function is available in extractor namespace."""
        tct = setup_namespace
        assert hasattr(tct.extractor, "extract_rosbag_feature")
        assert callable(tct.extractor.extract_rosbag_feature)

    def test_extract_dataframe_feature_function_exists(self, setup_namespace):
        """Test that extract_dataframe_feature function is available in extractor namespace."""
        tct = setup_namespace
        assert hasattr(tct.extractor, "extract_dataframe_feature")
        assert callable(tct.extractor.extract_dataframe_feature)

    def test_check_bag_topics_function_exists(self, setup_namespace):
        """Test that check_bag_topics function is available in extractor namespace."""
        tct = setup_namespace
        assert hasattr(tct.extractor, "check_bag_topics")
        assert callable(tct.extractor.check_bag_topics)

    def test_unpack_dataframe_and_show_topic_function_exists(self, setup_namespace):
        """Test that unpack_dataframe_and_show_topic function is available in extractor namespace."""
        tct = setup_namespace
        assert hasattr(tct.extractor, "unpack_dataframe_and_show_topic")
        assert callable(tct.extractor.unpack_dataframe_and_show_topic)

    def test_extractor_all_attribute(self, setup_namespace):
        """Test that extractor module has proper __all__ attribute."""
        tct = setup_namespace
        assert hasattr(tct.extractor, "__all__")
        assert isinstance(tct.extractor.__all__, list)
        assert len(tct.extractor.__all__) > 0


class TestTypingNamespaceModule:
    """Test the typing namespace module."""

    def test_typing_module_exists(self, setup_namespace):
        """Test that typing namespace exists."""
        tct = setup_namespace
        assert hasattr(tct, "typing")
        assert tct.typing is not None

    def test_trajectory_feature_dataclass_type_exists(self, setup_namespace):
        """Test that TrajectoryFeature type is available in typing namespace."""
        tct = setup_namespace
        assert hasattr(tct.typing, "TrajectoryFeature")

    def test_trajectory_feature_bag_dataclass_type_exists(self, setup_namespace):
        """Test that TrajectoryFeaturesBag type is available in typing namespace."""
        tct = setup_namespace
        assert hasattr(tct.typing, "TrajectoryFeaturesBag")

    def test_shadow_data_container_type_exists(self, setup_namespace):
        """Test that ShadowDataContainer type is available in typing namespace."""
        tct = setup_namespace
        assert hasattr(tct.typing, "ShadowDataContainer")


class TestMainNamespaceAPI:
    """Test the core API in the main namespace."""

    def test_common_exception_available(self, setup_namespace):
        """Test that TimestampCausalOrderingError is available in main namespace."""
        tct = setup_namespace
        assert hasattr(tct, "TimestampCausalOrderingError")
        assert tct.TimestampCausalOrderingError is not None

    def test_core_classes_available(self, setup_namespace):
        """Test that core abstract classes are available in main namespace."""
        tct = setup_namespace
        core_classes = [
            "AbstractTrajectoryFeature",
            "AbstractTrajectoryFeaturesBag",
            "AbstractTrajectoryStampedFeaturesBag",
            "AbstractTrajectoryArray",
            "BaseTrajectoryFeature",
            "NestedBaseTrajectory",
            "BaseTrajectoryArray",
        ]

        for class_name in core_classes:
            assert hasattr(tct, class_name), f"Missing core class: {class_name}"


class TestDataclassesNamespace:
    """Test that the dataclasses namespace works correctly."""

    def test_dataclasses_namespace_exists(self, setup_namespace):
        """Test that dataclasses namespace exists."""
        tct = setup_namespace
        assert hasattr(tct, "dataclasses")
        assert tct.dataclasses is not None

    def test_ros2_dataclasses_available_in_namespace(self, setup_namespace):
        """Test that ROS2 dataclasses are available in dataclasses namespace."""
        tct = setup_namespace
        ros2_dataclasses = [
            "NavMsgsOdometry",
            "SensorMsgsImu",
            "AckermannMsgsAckermannDriveStamped",
            "Tf2MsgsTFMessage",
            "VescMsgsVescImuStamped",
            "SensorMsgsLaserScan",
        ]

        for dataclass_name in ros2_dataclasses:
            assert hasattr(
                tct.dataclasses, dataclass_name
            ), f"Missing dataclass: {dataclass_name}"

    def test_abstract_classes_available_in_namespace(self, setup_namespace):
        """Test that abstract classes are available in dataclasses namespace."""
        tct = setup_namespace
        abstract_classes = [
            "AbstractTrajectoryFeature",
            "AbstractTrajectoryFeaturesBag",
            "AbstractTrajectoryStampedFeaturesBag",
            "AbstractTrajectoryArray",
        ]

        for class_name in abstract_classes:
            assert hasattr(
                tct.dataclasses, class_name
            ), f"Missing abstract class: {class_name}"

    def test_base_classes_available_in_namespace(self, setup_namespace):
        """Test that abstract classes are available in dataclasses namespace."""
        tct = setup_namespace
        abstract_classes = [
            "BaseTrajectoryFeature",
            "NestedBaseTrajectory",
            "BaseTrajectoryArray",
        ]

        for class_name in abstract_classes:
            assert hasattr(
                tct.dataclasses, class_name
            ), f"Missing base class: {class_name}"


class TestNamespacesConsistency:
    """Test that namespaces are consistent and properly structured."""

    def test_all_namespaces_have_all_attribute(self, setup_namespace):
        """Test that all namespace modules have __all__ attribute properly defined."""
        tct = setup_namespace
        namespaces = ["ros", "extractor", "factory", "temporal", "dataclasses", "utils"]

        for specialized_namespace in namespaces:
            namespace = getattr(tct, specialized_namespace)
            assert hasattr(
                namespace, "__all__"
            ), f"Missing __all__ in '{specialized_namespace}' specilized namespace"
            assert isinstance(
                namespace.__all__, list
            ), f"__all__ is not a list in '{specialized_namespace}' specilized namespace"
            assert (
                len(namespace.__all__) > 0
            ), f"Empty __all__ in '{specialized_namespace}' specilized namespace"

    def test_main_package_all_attribute(self, setup_namespace):
        """Test that main package has comprehensive __all__ attribute."""
        tct = setup_namespace
        assert hasattr(tct, "__all__")
        assert isinstance(tct.__all__, list)
        assert len(tct.__all__) > 0

        # Check that key sections are included
        expected_sections = [
            "__version__",
            "dataclasses",
            "extractor",
            "ros",
            "factory",
            "temporal",
            "typing",
            "utils",
        ]

        for item in expected_sections:
            assert item in tct.__all__, f"Missing item in main __all__: '{item}'"
