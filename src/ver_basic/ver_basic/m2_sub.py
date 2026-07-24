import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class M2_sub(Node):
    def __init__(self):
        super().__init__("m2_sub")
        # "message" 토픽 구독
        self.create_subscription(String, "message2", self.sub_callback, 10)

    def sub_callback(self, msg):
        self.get_logger().info(f"[m2_sub] 받은 메세지: {msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = M2_sub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()