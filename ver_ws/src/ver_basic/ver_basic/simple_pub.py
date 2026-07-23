import rclpy
from rclpy.node import Node
from std_msgs.msg import String

def timer_callback():
    print("첫번째 프로그램입니다.")

def main(args=None):
    rclpy.init(args=args) #rmw활성화
    node = Node("Message_pub") #노드이름
    #타이머 등록
    node.create_timer(1, timer_callback)
    pub = node.create_publisher(String, "message", 10)

    try:
        rclpy.spin(node) #블러(무한루프)
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()