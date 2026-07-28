# yaml 로 녹화 하는 모드
# ros2 service call \
#   /dynamixel_hardware_interface/set_dxl_torque \
#   std_srvs/srv/SetBool \
#   "{data: false}"
# 스페이스바 인식.
# yaml 파일을 저장

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import SetBool


class TeachManipulator(Node):
    JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4"]
    GRIPPER_JOINT = "gripper_left_joint"
    JOINT_LIMITS = {
        "joint1": [-3.14159265359, 3.14159265359],
        "joint2": [-1.5, 1.5],
        "joint3": [-1.5, 1.4],
        "joint4": [-1.7, 1.97],
    }
    GRIPPER_LIMITS = [-0.011, 0.02]

    def __init__(self):
        super().__init__("teach_manipulaotr")
        self.joint_state_subscription = self.create_subscription(
            JointState, "/joint_states", self.joint_state_callback, 10
        )
        # service call code
        self.torqu_service_client = self.create_client(
            SetBool, "dynamixel_hardware_interface/set_dxl_torque"
        )
        self.torqu_service_client.wait_for_service(timeout_sec=1.0)
        request = SetBool.Request()
        request.data = False
        future = self.torqu_service_client.call_async(request)
        future.add_done_callback(self.toque_response_callback)

    def joint_state_callback(self, msg: JointState):
        self.get_logger().info(f"{msg.position}")

    def toque_response_callback(self, future):
        response = future.result()
        if response is None or response.success:
            self.get_logger().info("실패")
        else:
            self.get_logger().info("성공")


def main(args=None):
    rclpy.init(args=args)
    node = TeachManipulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.try_shutdown()


if __name__ == "__main__":
    main()