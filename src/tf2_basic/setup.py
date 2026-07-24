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
        ],
    },
)