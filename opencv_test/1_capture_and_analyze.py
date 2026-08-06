import cv2
import time

# 1. 카메라 열기 및 WSL2 맞춤 설정 (초록 화면 예방)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 카메라 워밍업
for _ in range(10):
    cap.read()
    time.sleep(0.03)

orb = cv2.ORB_create(nfeatures=1000)
print("[1단계] 카메라 작동 중... 초록색 상자 안에 물체를 두고 's' 키를 눌러 캡처하세요.")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    h, w, _ = frame.shape
    # 중앙 가이드 영역 좌표
    roi_x1, roi_y1 = w // 4, h // 4
    roi_x2, roi_y2 = 3 * w // 4, 3 * h // 4

    # ROI 영역 추출 및 특징점 실시간 분석
    roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    kp = orb.detect(roi_gray, None)

    # 화면 시각화
    cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
    cv2.putText(frame, f"Live Keypoints: {len(kp)}", (roi_x1, roi_y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "Press 's' to Capture / 'q' to Quit", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("1. Real-time Capture & Analyze", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        # target.jpg 저장 및 최종 특징점 분석 보고
        cv2.imwrite("target.jpg", frame)
        print(f"\n[캡처 완료] 'target.jpg'가 저장되었습니다!")
        print(f" - 추출된 ORB 특징점 수: {len(kp)}개")
        break
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()