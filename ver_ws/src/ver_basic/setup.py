from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'ver_basic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob(os.path.join("launch",
        "*.launch.py"))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ver',
    maintainer_email='rooney010727@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'simple_pub = ver_basic.simple_pub:main',
            'class_pub = ver_basic.class_pub:main',   # m_pub (토픽: "message")
            'class_sub = ver_basic.class_sub:main',
            'header_pub = ver_basic.header_pub:main', # t_pub (토픽: "time")
            'm2_sub = ver_basic.m2_sub:main',         # 추가된 m2_sub
            'mt_sub = ver_basic.mt_sub:main',         # 추가된 mt_sub
            "mv_turtle = ver_basic.mv_turtle:main",
            "qos_test_pub = ver_basic.qos_test_pub:main",
            "qos_test_sub = ver_basic.qos_test_sub:main",
            "user_int_pub = ver_basic.user_int_pub:main",
            "service_server = ver_basic.service_server:main",
            "service_thread_server = ver_basic.service_thread_server:main",
            "service_client = ver_basic.service_client:main",
            "my_param = ver_basic.my_param:main",
            "param_async = ver_basic.param_async:main",
            "action_server = ver_basic.action_server:main",
        ],
    },
)
