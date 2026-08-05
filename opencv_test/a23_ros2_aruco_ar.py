import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from cv_bridge import CvBridge, CvBridgeError

import cv2
import numpy as np

class OpenManipulatorARNode(Node):
    def __init__(self):
        super().__init__('openmanipulator_ar_node')

        # 1. ROS 2 이미지 구독자 (Gazebo 카메라 토픽)
        # ※ 가제보 카메라 토픽 이름에 맞춰 수정하세요 (보통 /image_raw 또는 /camera/image_raw)
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        # 2. OpenManipulator 관절 제어 발행자 (ROS 2 Control)
        self.joint_pub = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        self.bridge = CvBridge()

        # 3. ArUco 사전 및 파라미터 설정 (OpenCV 버전 호환)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        
        try:
            self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        except AttributeError:
            self.detector = None # 구버전 OpenCV 대응

        # 4. 가상 카메라 매트릭스 (가제보 카메라 사양)
        self.camera_matrix = np.array([
            [600, 0, 320],
            [0, 600, 240],
            [0, 0, 1]
        ], dtype=np.float32)
        self.dist_coeffs = np.zeros((5, 1))

        self.MARKER_SIZE = 0.05 # 마커 크기: 5cm
        self.get_logger().info("OpenManipulator AR & Visual Servoing Node Started!")

    def draw_3d_cube(self, img, rvec, tvec):
        """ 마커 위에 3D AR 입체 큐브를 그리는 함수 """
        half = self.MARKER_SIZE / 2.0
        cube_points = np.float32([
            [-half, -half, 0], [half, -half, 0], [half, half, 0], [-half, half, 0],
            [-half, -half, -self.MARKER_SIZE], [half, -half, -self.MARKER_SIZE],
            [half, half, -self.MARKER_SIZE], [-half, half, -self.MARKER_SIZE]
        ])

        img_points, _ = cv2.projectPoints(cube_points, rvec, tvec, self.camera_matrix, self.dist_coeffs)
        img_points = np.int32(img_points).reshape(-1, 2)

        # 바닥면(파랑), 기둥(녹색), 천장면(빨강)
        img = cv2.drawContours(img, [img_points[:4]], -1, (255, 0, 0), 2)
        for i in range(4):
            img = cv2.line(img, tuple(img_points[i]), tuple(img_points[i+4]), (0, 255, 0), 2)
        img = cv2.drawContours(img, [img_points[4:]], -1, (0, 0, 255), 2)
        return img

    def image_callback(self, msg):
        try:
            # ROS 2 이미지 메시지를 OpenCV 이미지로 변환
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ArUco 마커 감지
        if self.detector is not None:
            corners, ids, _ = self.detector.detectMarkers(gray)
        else:
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.MARKER_SIZE, self.camera_matrix, self.dist_coeffs
            )

            for i in range(len(ids)):
                # 1. 3D 좌표축 표시
                cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvecs[i], tvecs[i], 0.03)
                # 2. 3D AR 큐브 표시
                frame = self.draw_3d_cube(frame, rvecs[i], tvecs[i])

                # 3. 마커와의 거리 계산 (카메라 기준 x, y, z)
                x_cam, y_cam, z_cam = tvecs[i][0]
                text = f"Target Pos -> X:{x_cam*100:.1f}cm, Y:{y_cam*100:.1f}cm, Z:{z_cam*100:.1f}cm"
                cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # TODO: 필요시 x_cam, y_cam 오차를 바탕으로 로봇 팔 회전 명령(JointTrajectory) 발행

        # 화면 출력
        cv2.imshow("Gazebo Eye-in-Hand AR Vision", frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = OpenManipulatorARNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()