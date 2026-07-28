import random
import rclpy
from action_msgs.msg import GoalStatus
from control_msgs.action import FollowJointTrajectory, GripperCommand
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint


class SequentialArmGripperActionClient(Node):

    def __init__(self):
        super().__init__("sequential_arm_gripper_action_client")

        # 1. 팔/그리퍼 액션 클라이언트
        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            "/arm_controller/follow_joint_trajectory",
        )
        self.gripper_client = ActionClient(
            self, GripperCommand, "/gripper_controller/gripper_cmd"
        )

        # 관절별 안전 각도 범위 (라디안)
        self.joint_limits = {
            "joint1": (-1.2, 1.2),
            "joint2": (-0.8, 0.4),
            "joint3": (-0.4, 0.8),
            "joint4": (-0.8, 0.8),
        }

        # 그리퍼 상태 관리 변수
        self.current_gripper_pos = 0.0  # 현재 그리퍼 위치 추적
        self.step_timer = None
        self.next_cycle_timer = None

        self.get_logger().info(
            "⏳ [순차 제어] 팔 이동 ↔ 그리퍼 천천히 동작 노드가 시작되었습니다!"
        )

        # 시작 타이머 (1초 후 서버 연결 체크 및 시작)
        self.init_timer = self.create_timer(1.0, self.check_server_and_start)

    def check_server_and_start(self):
        if not self.arm_client.wait_for_server(
            timeout_sec=1.0
        ) or not self.gripper_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("Action 서버 대기 중...")
            return

        # 최초 1회만 실행되도록 시작 타이머 해제
        self.init_timer.cancel()
        # 1단계: 팔 이동부터 시작
        self.move_arm_random()

    # =========================================================================
    # 🦾 [1단계] 팔 관절 랜덤 이동 (이 동안 그리퍼는 완전히 정지)
    # =========================================================================
    def move_arm_random(self):
        self.get_logger().info("🦾 [1단계] 팔 관절 이동 중... (그리퍼 정지)")

        rand_j1 = random.uniform(*self.joint_limits["joint1"])
        rand_j2 = random.uniform(*self.joint_limits["joint2"])
        rand_j3 = random.uniform(*self.joint_limits["joint3"])
        rand_j4 = random.uniform(*self.joint_limits["joint4"])
        duration = random.uniform(1.5, 2.5)

        point = JointTrajectoryPoint()
        point.positions = [rand_j1, rand_j2, rand_j3, rand_j4]
        point.time_from_start.sec = int(duration)
        point.time_from_start.nanosec = int(
            (duration - int(duration)) * 1_000_000_000
        )
        point.velocities = [0.0, 0.0, 0.0, 0.0]

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.header.stamp = self.get_clock().now().to_msg()
        goal.trajectory.joint_names = [
            "joint1",
            "joint2",
            "joint3",
            "joint4",
        ]
        goal.trajectory.points.append(point)

        send_goal_future = self.arm_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.arm_goal_response_callback)

    def arm_goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Arm Goal이 거절되었습니다. 1초 후 재시도합니다.")
            self.create_timer(1.0, self.move_arm_random)
            return

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.arm_result_callback)

    def arm_result_callback(self, future):
        result = future.result()
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                "✅ [1단계 완료] 팔 정지 완료 -> 0.5초 후 그리퍼 동작"
            )
            # 팔이 완벽히 멈춘 후 0.5초 뒤 2단계(그리퍼) 시작
            self.next_cycle_timer = self.create_timer(
                0.5, self.start_gripper_phase
            )

    def start_gripper_phase(self):
        self.next_cycle_timer.cancel()
        self.move_gripper_slowly()

    # =========================================================================
    # 🤏 [2단계] 그리퍼 천천히 동작 (이 동안 팔 관절은 완전히 정지)
    # =========================================================================
    def move_gripper_slowly(self):
        self.target_gripper_pos = random.uniform(-0.01, 0.01)
        self.start_gripper_pos = self.current_gripper_pos
        self.step_count = 0
        self.total_steps = 20  # 20단계로 분할

        self.get_logger().info(
            f"🤏 [2단계] 그리퍼 서서히 이동 시작... (목표: {self.target_gripper_pos:.3f}m, 팔 정지)"
        )

        # 0.1초마다 조금씩 목표 지점으로 이동 (총 2.0초 소요)
        self.step_timer = self.create_timer(0.1, self.step_gripper_callback)

    def step_gripper_callback(self):
        self.step_count += 1
        ratio = self.step_count / self.total_steps

        # 시작 위치에서 목표 위치까지 선형 보간 (조금씩 분할 이동)
        interpolated_pos = self.start_gripper_pos + ratio * (
            self.target_gripper_pos - self.start_gripper_pos
        )

        goal = GripperCommand.Goal()
        goal.command.position = interpolated_pos
        goal.command.max_effort = 0.0
        self.gripper_client.send_goal_async(goal)

        # 20단계 이동 완료 시
        if self.step_count >= self.total_steps:
            self.step_timer.cancel()  # 그리퍼 스텝 타이머 종료
            self.current_gripper_pos = self.target_gripper_pos
            self.get_logger().info(
                "✅ [2단계 완료] 그리퍼 동작 완료 -> 0.5초 후 다시 팔 이동"
            )

            # 그리퍼 이동 완료 후 0.5초 뒤 다시 1단계(팔 관절 이동) 시작
            self.next_cycle_timer = self.create_timer(
                0.5, self.start_arm_phase
            )

    def start_arm_phase(self):
        self.next_cycle_timer.cancel()
        self.move_arm_random()


def main(args=None):
    rclpy.init(args=args)
    node = SequentialArmGripperActionClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("사용자에 의해 중지되었습니다.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()