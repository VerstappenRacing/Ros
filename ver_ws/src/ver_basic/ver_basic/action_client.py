import time

import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionServer
from rcply.action.client import ClientGoalHandle
from rclpy.action.server import ServerGoalHandle
from rclpy.node import Node
from rclpy.node import Future
from user_interface.action import Fibonacci


class Action_client(Node):
    def __init__(self):
        super().__init__("action_client")
        self.action_client = ActionClient(
            self, Fibonacci, "fibonacci_server",
        )
    def send_goal(self, step: str):
        goal_msg: = Fibonacci.Goal()
        goal_msg.step = step
        #서버에 접속하기()
        self.action_client.wait_for_server(timeout_sec=1)
        #request 보내기 -> goal 보내기
        self.future = self.action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self.future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future:Future):
        goal_handle: ClientGoalHandle = future.result()
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)
        pass

    def feedback_callback(self, mgs:Fibonacci.Feedback):
        pass

    def get_result_callback(self, future: Future):
        pass


def main(args=None):
    rclpy.init(args=args)  # rmw 활성화
    node = Action_server()
    try:
        rclpy.spin(node)  # 블럭 (무한 루프)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()