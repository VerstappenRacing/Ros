import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    usb_port = LaunchConfiguration('usb_port', default='/dev/ttyUSB0')
    baud_rate = LaunchConfiguration('baud_rate', default='1000000')

    # 1. 실물 로봇팔 제어 노드 실행
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('open_manipulator_bringup'),
                'launch',
                'open_manipulator_x.launch.py'
            )
        ]),
        launch_arguments={
            'usb_port': usb_port,
            'baud_rate': baud_rate
        }.items()
    )

    # 2. RViz2 시뮬레이션 및 MoveIt 실행
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('open_manipulator_moveit_config'),
                'launch',
                'demo.launch.py'
            )
        ])
    )

    return LaunchDescription([
        DeclareLaunchArgument('usb_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('baud_rate', default_value='1000000'),
        bringup_launch,
        moveit_launch
    ])