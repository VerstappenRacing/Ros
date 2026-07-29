import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'tf2_basic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ver',
    maintainer_email='rooney010727@gmail.com',
    description='tf2 basic code for tutorial',
    license='Apache 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'static_turtle_tf2_broadcaster = tf2_basic.static_turtle_tf2_broadcaster:main',
            'dynamic_turtle_tf2_broadcaster = tf2_basic.dynamic_turtle_tf2_broadcaster:main',
            'tf_listener = tf2_basic.tf_listener:main',
            "turtle_tf_listener = tf2_basic.turtle_tf_listener:main",
            "move_u2d2 = tf2_basic.move_u2d2:main",
            "move_manipulator = tf2_basic.move_manipulator:main",
            "move_manipulator_action = tf2_basic.move_manipulator_action:main",
            'wave_arm_action = tf2_basic.wave_arm_action:main',
            "dance_manipulator = tf2_basic.dance_manipulator:main",
            "play_recorded_dance = tf2_basic.play_recorded_dance:main",
            "teach_manipulator = tf2_basic.teach_manipulator:main",
            "moveit_test = tf2_basic.moveit_test:main",
            "moveit_class = tf2_basic.moveit_class:main",
        ],
    },
)