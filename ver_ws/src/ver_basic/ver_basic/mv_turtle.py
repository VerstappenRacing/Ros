import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute, SetPen

class MvTurtleFakerShh(Node):
    def __init__(self):
        super().__init__('mv_turtle_faker_shh')
        
        # 1. 좌표 이동 및 펜 제어 서비스 클라이언트
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')

        while not self.teleport_client.wait_for_service(timeout_sec=1.0) or not self.pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('turtlesim 서비스 대기 중...')

        self.get_logger().info('🤫 페이커(Faker)의 시그니처 "쉿!" 표정을 그립니다!')
        
        # 적절한 그리기 속도 (0.12초 간격)
        self.timer = self.create_timer(0.12, self.draw_step)

        # 페이커 '쉿' 포즈 스트로크 데이터 (각 획의 좌표 묶음)
        self.strokes = [
            # 1. 얼굴 윤곽 및 귀 (Head & Ears)
            [
                (5.5, 3.0), (4.0, 4.2), (3.6, 5.0), (3.4, 5.3), (3.6, 5.6), (3.8, 5.2),
                (3.8, 6.8), (3.6, 7.5), (4.5, 8.2), (5.5, 8.4), (6.5, 8.2), (7.4, 7.5),
                (7.2, 6.8), (7.4, 5.2), (7.6, 5.6), (7.8, 5.3), (7.4, 5.0), (7.0, 4.2), (5.5, 3.0)
            ],
            
            # 2. 앞머리 헤어 라인 (Hair Fringe)
            [
                (3.8, 6.8), (4.4, 6.5), (4.8, 7.1), (5.5, 6.6), (6.2, 7.1), (6.8, 6.5), (7.2, 6.8)
            ],

            # 3. 시그니처 안경 - 왼쪽 알 (Left Glasses Frame)
            [
                (5.0, 6.0), (5.0, 5.3), (3.9, 5.3), (3.9, 6.3), (5.0, 6.3), (5.0, 6.0)
            ],

            # 4. 안경 다리 & 브릿지 (Bridge & Temples)
            [ (5.0, 6.0), (6.0, 6.0) ], # 브릿지
            [ (3.9, 6.0), (3.5, 6.0) ], # 왼쪽 안경다리
            [ (7.1, 6.0), (7.5, 6.0) ], # 오른쪽 안경다리

            # 5. 시그니처 안경 - 오른쪽 알 (Right Glasses Frame)
            [
                (6.0, 6.0), (6.0, 5.3), (7.1, 5.3), (7.1, 6.3), (6.0, 6.3), (6.0, 6.0)
            ],

            # 6. 눈썹 & 카리스마 눈빛 (Eyebrows & Eyes)
            [ (4.1, 6.6), (4.9, 6.5) ], # 왼쪽 눈썹
            [ (6.1, 6.5), (6.9, 6.6) ], # 오른쪽 눈썹
            [ (4.2, 5.8), (4.8, 5.8) ], # 왼쪽 눈
            [ (6.2, 5.8), (6.8, 5.8) ], # 오른쪽 눈

            # 7. 코 (Nose)
            [ (5.5, 5.8), (5.5, 5.0), (5.3, 4.8) ],

            # 8. 입술 양옆 라인 (Mouth behind finger)
            [ (4.6, 4.2), (5.2, 4.2) ],
            [ (5.8, 4.2), (6.4, 4.2) ],

            # 9. ★ 핵심: 쉿! 검지 손가락 (Index Finger over Lips)
            [
                (5.2, 1.8), (5.2, 4.8), (5.5, 5.2), (5.8, 4.8), (5.8, 1.8)
            ],
            # 손가락 마디 주름 (Finger Joint Lines)
            [ (5.3, 4.0), (5.7, 4.0) ],
            [ (5.3, 3.3), (5.7, 3.3) ],
            # 접힌 주먹/손 밑부분 (Hand base)
            [ (4.5, 1.8), (6.5, 1.8) ]
        ]

        self.stroke_idx = 0
        self.point_idx = 0
        self.is_pen_down = False

    def set_pen(self, off, r=255, g=255, b=255, width=3):
        req = SetPen.Request()
        req.r = r
        req.g = g
        req.b = b
        req.width = width
        req.off = 1 if off else 0
        self.pen_client.call_async(req)

    def draw_step(self):
        if self.stroke_idx >= len(self.strokes):
            # 모두 그린 후 펜 올리고 완료
            self.set_pen(off=True)
            self.get_logger().info('🤫 "쉿! 대상혁(Faker)" 완성을 축하합니다!')
            self.timer.cancel()
            return

        current_stroke = self.strokes[self.stroke_idx]

        # 새 스트로크 시작 지점으로 이동 시 펜 올리기
        if self.point_idx == 0:
            self.set_pen(off=True) # 펜 올림 (이동선 안 보임)
            x, y = current_stroke[0]
            
            req = TeleportAbsolute.Request()
            req.x = float(x)
            req.y = float(y)
            req.theta = 0.0
            self.teleport_client.call_async(req)
            
            self.point_idx = 1
            return

        # 스트로크 내부 점들 그리기
        if self.point_idx == 1 and not self.is_pen_down:
            self.set_pen(off=False, r=255, g=255, b=255, width=3) # 하얀색 펜 내림

        x, y = current_stroke[self.point_idx]
        req = TeleportAbsolute.Request()
        req.x = float(x)
        req.y = float(y)
        req.theta = 0.0
        self.teleport_client.call_async(req)

        self.point_idx += 1

        # 현재 스트로크 완료 시 다음 스트로크로 넘어가기
        if self.point_idx >= len(current_stroke):
            self.stroke_idx += 1
            self.point_idx = 0
            self.is_pen_down = False

def main(args=None):
    rclpy.init(args=args)
    node = MvTurtleFakerShh()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()