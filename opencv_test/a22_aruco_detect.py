from pathlib import Path
import cv2

def main():
    file_path = Path(__file__).parent
    pipeline = (
        "v4l2src device=/dev/video0 ! "
        "image/jpeg, width=640, height=480, framerate=30/1 ! "
        "jpegdec ! "
        "videoconvert ! "
        "video/x-raw, format=BGR ! "
        "appsink drop=true sync=false"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다. 파이프라인을 확인해 주세요.")
        return

    # ArUco dictionary & parameters
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters_create()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 불러오지 못했습니다.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()