import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


class CameraPub(Node):

    def __init__(self):
        super().__init__("camera_pub")

        self.publisher_ = self.create_publisher(Image, "camera/image_raw", 10)
        self.publisher_info = self.create_publisher(
            CameraInfo, "camera/camera_info", 10
        )
        self.bridge = CvBridge()

        self.width = 640
        self.height = 480
        self.window_name = "Camera Stream"

        # 💡 카메라 장치 번호 (0이 안 되면 2로 변경해 보세요!)
        CAM_INDEX = 0

        self.get_logger().info(
            f"카메라 (index: {CAM_INDEX}) 연결 시도 중..."
        )
        self.cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)

        # 해상도 설정
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self.cap.isOpened():
            self.get_logger().error(
                f"카메라({CAM_INDEX}번)를 열 수 없습니다! CAM_INDEX 번호를 변경해 보세요."
            )
            return

        self.get_logger().info(
            "카메라 연결 성공! 화면 창을 생성합니다."
        )
        cv2.namedWindow(self.window_name)

        self.camera_info = self.create_camera_info()
        self.timer = self.create_timer(1 / 30, self.img_gen_callback)

    def create_camera_info(self):
        msg = CameraInfo()
        msg.width = self.width
        msg.height = self.height
        msg.distortion_model = "plumb_bob"
        msg.d = [0.0, 0.0, 0.0, 0.0, 0.0]

        fx = fy = 600.0
        cx = self.width / 2.0
        cy = self.height / 2.0

        msg.k = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
        msg.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        msg.p = [fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
        return msg

    def img_gen_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warning("프레임을 읽을 수 없습니다.")
            return

        # 사각형 그리기
        cv2.rectangle(
            frame,
            (10, 10),
            (self.width - 10, self.height - 10),
            (255, 0, 0),
            3,
        )

        cv2.imshow(self.window_name, frame)
        key = cv2.waitKey(1) & 0xFF

        now = self.get_clock().now().to_msg()

        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        img_msg.header.stamp = now
        img_msg.header.frame_id = "camera_link"

        self.camera_info.header.stamp = now
        self.camera_info.header.frame_id = "camera_link"

        self.publisher_.publish(img_msg)
        self.publisher_info.publish(self.camera_info)

        if key == ord("q"):
            self.get_logger().info("'q' 키 입력으로 종료합니다.")
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = CameraPub()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        if hasattr(node, "cap") and node.cap.isOpened():
            node.cap.release()
        cv2.destroyAllWindows()
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()