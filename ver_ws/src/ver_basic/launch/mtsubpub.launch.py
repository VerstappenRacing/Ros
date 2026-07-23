from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package="ver_basic", executable="mpub"),
            Node(package="ver_basic", executable="tpub"),
            Node(package="ver_basic", executable="msub"),
            Node(package="ver_basic", executable="m2sub"),
            Node(package="ver_basic", executable="mtsub"),
        ]
    )