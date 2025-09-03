# coding=utf-8
from matplotlib import pyplot as plt


def plot_trajectory_2d(trajectory_data):
    """Plot 2D trajectory with start and end points."""
    x_pos = trajectory_data.topic_odom.pose_pose_position_x
    y_pos = trajectory_data.topic_odom.pose_pose_position_y

    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot trajectory
    ax.plot(x_pos, y_pos, 'b-', linewidth=2, alpha=0.8, label='Trajectory')

    # Mark start and end points
    ax.scatter(x_pos[0], y_pos[0], color='green', s=150, marker='o',
               label='Start', edgecolor='black', linewidth=2, zorder=5)
    ax.scatter(x_pos[-1], y_pos[-1], color='red', s=150, marker='s',
               label='End', edgecolor='black', linewidth=2, zorder=5)

    # Add direction arrows
    skip = max(1, len(x_pos) // 100)
    for i in range(skip, len(x_pos) - skip, skip):
        dx = x_pos[i + skip // 2] - x_pos[i - skip // 2]
        dy = y_pos[i + skip // 2] - y_pos[i - skip // 2]
        ax.arrow(x_pos[i], y_pos[i], dx * 0.01, dy * 0.01,
                 head_width=0.35, head_length=0.35, fc='orange', ec='orange', alpha=0.7)

    ax.set_xlabel('X Position (m)', fontsize=12)
    ax.set_ylabel('Y Position (m)', fontsize=12)
    ax.set_title(trajectory_data.dataset_info, fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    return fig, ax


