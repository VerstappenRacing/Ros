import rclpy
from action_msgs.msg import GoalStatus
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint


class AlignHomeNode(Node):

    def __init__(self):
        super().__init__("align_home_node")
        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            "/arm_controller/follow_joint_trajectory",
        )
        self.get_logger().info("📐 관절 안전 회전 테스트 시작...")
        self.timer = self.create_timer(1.0, self.send_home_pose)

    def send_home_pose(self):
        if not self.arm_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("Arm Action 서버 대기 중...")
            return

        self.timer.cancel()

        point = JointTrajectoryPoint()
        # 안전 한계 범위 안의 각도: 1.57 rad (90도 회전)
        # 만약 반대 방향으로 돌리고 싶다면 -1.57 을 넣으세요.
        point.positions = [
            1.57,
            0.0,
            0.0,
            0.0,
        ]  # [joint1, joint2, joint3, joint4]
        point.time_from_start.sec = 3

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = [
            "joint1",
            "joint2",
            "joint3",
            "joint4",
        ]
        goal.trajectory.points.append(point)

        self.get_logger().info(
            "🚀 joint1을 1.57 rad (90도) 방향으로 회전시킵니다."
        )

        send_goal_future = self.arm_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("❌ 명령이 거절되었습니다.")
            return

        self.get_logger().info("✅ 명령 승인됨! 이동 시작...")


def main(args=None):
    rclpy.init(args=args)
    node = AlignHomeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("중지되었습니다.")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()