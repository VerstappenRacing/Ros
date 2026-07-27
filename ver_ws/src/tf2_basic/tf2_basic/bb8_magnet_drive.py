import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class BB8MagnetDrive(Node):
    def __init__(self):
        super().__init__('bb8_magnet_drive')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.03, self.timer_callback) # 33Hz
        
        self.body_roll_pos = 0.0
        self.head_yaw_pos = 0.0
        self.time_counter = 0.0

    def timer_callback(self):
        self.time_counter += 0.03
        
        # 1. 몸통은 굴러가며 이동 (Pitch 축 지속 회전)
        speed = 0.15 # 주행 속도
        self.body_roll_pos += speed
        
        # 2. 머리는 자석에 의해 꼭대기에 고정된 채, 호기심 있게 좌우 탐색 (Yaw 축)
        #    이동 시 머리가 진행 방향을 고정하여 바라봄
        self.head_yaw_pos = math.sin(self.time_counter * 1.5) * 0.4
        
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['body_roll_joint', 'head_yaw_joint']
        msg.position = [self.body_roll_pos, self.head_yaw_pos]
        
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BB8MagnetDrive()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()