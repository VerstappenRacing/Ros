# sudo usermod -aG video $USER
# sudo chmod 666 /dev/video0
# sudo chmod 666 /dev/video1
from pathlib import Path

import cv2


def main():
    file_path = Path(__file__).parent
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("balck", frame)
        if cv2.waitKey(1) == ord("q"):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()