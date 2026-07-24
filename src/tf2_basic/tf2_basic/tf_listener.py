# ros2 run turtlesim turtlesim_node
# rviz2
# ros2 run tf2_basic dynamic_turtle_tf2_broadcaster
# ros2 run tf2_basic tf_listener
# ros2 run tf2_basic static_turtle_tf2_broadcaster
# ros2 run turtlesim turtle_teleop_key

import rclpy
from rclpy.node import Node
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class FrameListener(Node):
    def __init__(self):
        super().__init__('tf_listener')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(0.5, self.on_timer)

    def on_timer(self):
        try:
            t = self.tf_buffer.lookup_transform('world', 'turtle1', rclpy.time.Time())
            self.get_logger().info(f'turtle1 pos -> x: {t.transform.translation.x:.2f}, y: {t.transform.translation.y:.2f}')
        except TransformException as ex:
            self.get_logger().info(f'Transform waiting: {ex}')

def main(args=None):
    rclpy.init(args=args)
    node = FrameListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()