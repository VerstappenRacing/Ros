import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class BB8Mover(Node):
    def __init__(self):
        super().__init__('bb8_mover')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.05, self.timer_callback) # 20Hz
        self.angle = 0.0

    def timer_callback(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['base_to_body', 'head_joint']
        
        # 시간에 따라 몸통은 지속적으로 구르고, 머리는 좌우로 살랑살랑 회전
        self.angle += 0.05
        body_pos = self.angle % (2 * math.pi)
        head_pos = math.sin(self.angle * 2) * 0.8  # 좌우 약 45도 범주 회전
        
        msg.position = [body_pos, head_pos]
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BB8Mover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
