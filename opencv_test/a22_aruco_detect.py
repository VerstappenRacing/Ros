import cv2

# video0부터 video3까지 차례대로 화면 열기 시도
for dev_id in range(4):
    print(f"\n[알림] /dev/video{dev_id} 테스트 시작...")
    cap = cv2.VideoCapture(dev_id, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print(f" -> /dev/video{dev_id}: 장치를 열 수 없음")
        continue

    # 카메라 포맷 설정 (MJPEG 포맷 강제 지정)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ret, frame = cap.read()
    if ret and frame is not None:
        print(f"★ /dev/video{dev_id} 연결 성공! 화면이 열립니다.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(f"Camera (/dev/video{dev_id})", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        break
    else:
        print(f" -> /dev/video{dev_id}: 영상 데이터를 읽을 수 없음")
    
    cap.release()