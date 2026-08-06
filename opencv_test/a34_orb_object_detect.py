import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np
import os
import time

class ORBObjectDetector(Node):
    def __init__(self):
        super().__init__('orb_object_detector')
        self.get_logger().info("★ ORB 실시간 물체 추적 노드 시작 중...")

        # 1. ROS 2 카메라 영상 발행자 (다른 노드가 이 영상을 볼 수 있도록 토픽도 같이 발행)
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()

        # 2. ORB 검출기 및 매처 생성
        self.orb = cv2.ORB_create(nfeatures=1500)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

        # 3. 타겟 이미지(target.jpg) 읽기
        target_path = 'target.jpg'
        if not os.path.exists(target_path):
            self.get_logger().error("'target.jpg' 파일이 없습니다! 먼저 capture_target.py를 실행하여 사진을 찍으세요.")
            raise FileNotFoundError("target.jpg 파일 없음")

        self.target_gray = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
        self.kp_target, self.des_target = self.orb.detectAndCompute(self.target_gray, None)
        self.get_logger().info(f"타겟 이미지 로드 완료 (특징점 수: {len(self.kp_target)}개)")

        # 4. 웹캠 직접 연결 (WSL2 초록 화면 및 즉시 종료 방지 설정)
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cap.isOpened():
            self.get_logger().error("카메라를 열 수 없습니다. /dev/video* 권한이나 usbipd 연결을 확인하세요.")
            raise RuntimeError("카메라 열기 실패")

        # 워밍업 (초기 불량 프레임 비우기)
        for _ in range(10):
            self.cap.read()
            time.sleep(0.03)

        self.get_logger().info("★ 카메라 준비 완료! 실시간 추적 화면을 표시합니다.")

        # 5. 실시간 루프 타이머 설정 (약 30 FPS)
        self.timer = self.create_timer(0.033, self.process_frame)

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return

        # 다른 ROS 2 노드에서도 볼 수 있도록 토픽 발행
        try:
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            self.image_pub.publish(img_msg)
        except Exception as e:
            pass

        # ORB 특징점 검출
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_frame, des_frame = self.orb.detectAndCompute(frame_gray, None)

        if des_frame is not None and len(kp_frame) > 0 and self.des_target is not None:
            matches = self.bf.knnMatch(self.des_target, des_frame, k=2)

            # Lowe's Ratio Test
            good_matches = []
            for match in matches:
                if len(match) == 2:
                    m, n = match
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)

            # 유효 매칭점 12개 이상 시 물체 위치 윤곽선 추적
            if len(good_matches) >= 12:
                src_pts = np.float32([self.kp_target[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if M is not None:
                    h, w = self.target_gray.shape
                    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                    dst = cv2.perspectiveTransform(pts, M)

                    # 감지된 물체 영역 초록색 테두리 표시
                    frame = cv2.polylines(frame, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)
                    
                    cv2.putText(frame, f"TARGET MATCHED! ({len(good_matches)} pts)", (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f"Searching... ({len(good_matches)}/12)", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 실시간 추적 창 표시
        cv2.imshow("ORB Real-time Object Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            rclpy.shutdown()

    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    try:
        node = ORBObjectDetector()
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()