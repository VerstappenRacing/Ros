import cv2
import time

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# MJPG 코덱 지정 (초록 화면 방지)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 워밍업
for _ in range(10):
    cap.read()
    time.sleep(0.03)

print("[알림] 's' 키: target.jpg 저장 / 'q' 키: 종료")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    h, w, _ = frame.shape
    cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
    cv2.putText(frame, "Press 's' to capture target", (30, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Capture Target Image", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        cv2.imwrite("target.jpg", frame)
        print("★ target.jpg 저장 성공!")
        break
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()