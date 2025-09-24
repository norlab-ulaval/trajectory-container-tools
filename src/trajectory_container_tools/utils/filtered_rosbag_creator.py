import os
from pathlib import Path

from rosbags.highlevel import AnyReader
from rosbags.rosbag2 import Reader, Writer
from typing import List, Optional, Union

from tqdm import tqdm

from trajectory_container_tools import check_rosbag_path_and_show_available_topics
from trajectory_container_tools.rosbag_to_tct import check_rosbag_path
from trajectory_container_tools.utils.ros2_non_native_msg import (
    register_ros2_non_native_msg,
    )
from trajectory_container_tools.utils.ros2_utils import get_rosbag_typestore_auto_distro


def create_filtered_rosbag(
        input_rosbag_path: Union[str, Path],
        output_rosbag_path: Union[str, Path],
        selected_topics: List[str],
        start: Optional[int] = None,
        stop: Optional[int] = None,
        ) -> Path:
    """
    Create a smaller rosbag by filtering topics and timestamp intervals.

    This function reads from an input rosbag and creates a new rosbag containing only the
    specified topics within the given timestamp range.

    :param input_rosbag_path: Path to the input ROS bag file.
    :param output_rosbag_path: Path where the filtered ROS bag will be created.
    :param selected_topics: List of topic names to include in the filtered rosbag.
    :param start: Optional start time for filtering messages, in nanoseconds.
    :param stop: Optional stop time for filtering messages, in nanoseconds.
    :return: Path to the created filtered rosbag.
    """
    input_path = Path(input_rosbag_path)
    output_path = Path(output_rosbag_path)

    # Ensure input rosbag exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input rosbag not found: {input_path}")

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    typestore = get_rosbag_typestore_auto_distro()
    typestore = register_ros2_non_native_msg(typestore)

    with Reader(input_path) as reader:
        # Filter connections for selected topics
        selected_connections = [
                conn for conn in reader.connections if conn.topic in selected_topics
                ]

        if not selected_connections:
            raise ValueError(
                    f"None of the specified topics {selected_topics} found in rosbag"
                    )

        print(f"[TCT] Creating filtered rosbag with {len(selected_connections)} topics")
        for conn in selected_connections:
            print(f"  Including topic: {conn.topic} ({conn.msgtype})")

        with Writer(output_path, version=9) as writer:
            # Add connections for selected topics
            connection_map = {}
            for connection in selected_connections:
                conn_id = writer.add_connection(
                        connection.topic,
                        connection.msgtype,
                        typestore=typestore,
                        # serialization_format=connection.serialization_format,
                        # offered_qos_profiles=connection.offered_qos_profiles
                        )
                connection_map[connection.id] = conn_id

            # Copy filtered messages
            message_count = 0
            print("[TCT] Copying messages...")

            for connection, timestamp, rawdata in tqdm(
                    reader.messages(
                            connections=selected_connections, start=start, stop=stop
                            ),
                    desc="[TCT] Writing filtered messages",
                    ):
                if connection.id in connection_map:
                    writer.write(connection_map[connection.id], timestamp, rawdata)
                    message_count += 1

            print(f"[TCT] Filtered rosbag created with {message_count} messages")
            print(f"[TCT] Output saved to: {output_path}")

    return output_path


if __name__ == "__main__":
    rosbag_start = None
    rosbag_stop = None

    # .... Path to ROS bag in 'shared_data' directory ...........................................

    # BAG = "2024-03-21_12-19-00" # small circle
    # BAG = "2024-03-21_12-23-53" # medium spiral

    BAG = "2024-03-21_14-52-35"  # ★★ 8408 timesteps
    rosbag_start = 1711047206000000000
    rosbag_stop = 1711047237203288917

    # BAG = "2024-03-21_15-14-09"  # ★★ 63063 timesteps
    # BAG = "2024-03-21_15-26-13" # ★ 35128 timesteps
    # BAG = "2024-03-21_15-35-28" # ★ 179236 timesteps
    rosbag_path = os.path.join(
            "data", "shared_data", "rosbag-vaul-f110-grand-salon-raw-msg", BAG
            )

    target_destination = os.path.join("data", "repository_data")
    target_destination = check_rosbag_path(target_destination)
    target_rosbag_path = os.path.join(target_destination, "tests_data",
                                      "rosbag-vaul-f110-grand-salon-raw-msg", f"{BAG}-filtered")

    # .............................................................................................
    rosbag_path = check_rosbag_path_and_show_available_topics(rosbag_path)

    create_filtered_rosbag(
            input_rosbag_path=rosbag_path,
            output_rosbag_path=target_rosbag_path,
            selected_topics=[
                    "/teleop",
                    "/odom",
                    "/sensors/imu/raw",
                    "/scan",
                    ],
            start=rosbag_start,
            stop=rosbag_stop,
            )
