# ros2 run turtlesim turtlesim_node
# rviz2
# ros2 run tf2_basic dynamic_turtle_tf2_broadcaster
# ros2 run tf2_basic tf_listener
# ros2 run tf2_basic static_turtle_tf2_broadcaster
# ros2 run turtlesim turtle_teleop_key

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.duration import Duration
from rclpy.node import Node
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class FrameListener(Node):
    def __init__(self):
        super().__init__('dynamic_tf')
        self.target_frame = (self.declare_parameter("target_frame", "joint2").get_parameter_value().string_value)
        self.source_frame = (self.declare_parameter("source_frame", "world").get_parameter_value().string_value)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        t = TransformStamped = self.tf_buffer.lookup_transfrom(self.target_frame, self.source_frame, Time(), timeout=Duration(seconds=1.0))
        self.get_logger().info(f"{t}")

def main(args=None):
    rclpy.init(args=args)
    node = M_pub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()
        

if __name__ == '__main__':
    main()