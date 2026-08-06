import cv2
import numpy as np
import os
import time

# 1. 캡처된 타겟 이미지 불러오기 및 ORB 분석
target_path = 'target.jpg'
if not os.path.exists(target_path):
    print("[에러] 'target.jpg' 파일이 없습니다. 1단계를 먼저 실행하세요!")
    exit()

target_gray = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
orb = cv2.ORB_create(nfeatures=1500)
kp_target, des_target = orb.detectAndCompute(target_gray, None)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

# 2. 카메라 실행 및 설정
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

for _ in range(10):
    cap.read()
    time.sleep(0.03)

print("[2단계] 실시간 검증 시작... 카메라로 캡처한 물체를 보여주세요. ('q' 키: 종료)")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp_frame, des_frame = orb.detectAndCompute(frame_gray, None)

    is_matched = False
    match_score = 0

    if des_frame is not None and len(kp_frame) > 0 and des_target is not None:
        matches = bf.knnMatch(des_target, des_frame, k=2)

        # Lowe's Ratio Test (유효 매칭 필터링)
        good_matches = []
        for m_tuple in matches:
            if len(m_tuple) == 2:
                m, n = m_tuple
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

        match_score = len(good_matches)

        # 유효 매칭점이 15개 이상일 때 동일 물체로 인정
        if match_score >= 15:
            src_pts = np.float32([kp_target[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if M is not None:
                is_matched = True
                h, w = target_gray.shape
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)

                # 물체 테두리에 초록색 박스 그리기
                frame = cv2.polylines(frame, [np.int32(dst)], True, (0, 255, 0), 3)

    # 대조 결과 상단 바 출력
    if is_matched:
        cv2.rectangle(frame, (0, 0), (640, 50), (0, 180, 0), -1)
        cv2.putText(frame, f"[VERIFIED] MATCHED! (Score: {match_score})", (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    else:
        cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 180), -1)
        cv2.putText(frame, f"[SEARCHING] UNMATCHED (Score: {match_score}/15)", (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("2. Real-time Verification & Match", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()