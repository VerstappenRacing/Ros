import os
from glob import glob

from setuptools import find_packages, setup

package_name = "ver_basic"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob(os.path.join("launch", "*.launch.py"))),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="ver",
    maintainer_email="rooney010727@gmail.com",
    description="TODO: Package description",
    license="Apache 2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "simple_pub = ver_basic.simple_pub:main",
            "class_pub = ver_basic.class_pub:main",
            "class_sub = ver_basic.class_sub:main",
            "header_pub = ver_basic.header_pub:main",
            "mpub = ver_basic.mpub:main",
            "tpub = ver_basic.tpub:main",
            "msub = ver_basic.msub:main",
            "m2sub = ver_basic.m2sub:main",
            "mtsub = ver_basic.mtsub:main",
            "mv_turtle = ver_basic.mv_turtle:main",
            "qos_test_pub = ver_basic.qos_test_pub:main",
            "qos_test_sub = ver_basic.qos_test_sub:main",
            "user_int_pub = ver_basic.user_int_pub:main",
            "service_server = ver_basic.service_server:main",
        ],
    },
)