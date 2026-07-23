import rclpy
from rclpy.node import Node
from user_interface.msg import UserInt

class M_pub(Node):
    def __init__(self):
        super().__init__("massage_pub") # 노드 이름
        # 타이머 등록
        self.create_timer(1, self.timer_callback)
        self.pub = self.create_publisher(UserInt, "message1", 10)

    def timer_callback(self):
        msg = UserInt() # DDS 에 보낼 객체 초기화
        msg.header.frame_id = "time test"
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.user_int = 12
        msg.user_int2 = 23
        msg.user_int3 = 53
        self.pub.publish(msg) #DDS로 보내는 기능 수행

def main(args=None):
    rclpy.init(args=args) #rmw활성화x
    node = M_pub()
    try:
        rclpy.spin(node) #블러(무한루프)
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()