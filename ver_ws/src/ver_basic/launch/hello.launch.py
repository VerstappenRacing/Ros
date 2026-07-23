from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='ver_basic', executable='class_pub'),   # /massage_pub
        Node(package='ver_basic', executable='class_sub'),   # /massage_sub
        Node(package='ver_basic', executable='m2_sub'),      # /m2_sub
        Node(package='ver_basic', executable='header_pub'),  # /time_pub (수정된 노드가 실행됨)
        Node(package='ver_basic', executable='mt_sub'),      # /mt_sub
    ])