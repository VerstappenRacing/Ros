import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Header

class MT_sub(Node):
    def __init__(self):
        super().__init__("mt_sub")
        
        # 1. message 토픽 구독
        self.create_subscription(String, "message1", self.m_callback, 10)
        
        # 2. time 토픽 구독 (⭕ 여기가 "time"으로 적혀있어야 합니다!)
        self.create_subscription(Header, "time", self.t_callback, 10)

    def m_callback(self, msg):
        self.get_logger().info(f"[mt_sub] (m): {msg.data}")

    def t_callback(self, msg):
        self.get_logger().info(f"[mt_sub] (t): {msg.stamp.sec}")

def main(args=None):
    rclpy.init(args=args)
    node = MT_sub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()