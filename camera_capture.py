import cv2
import os
import time


def open_camera():
    """
    Try to find an available camera index.
    """

    for idx in range(3):

        cap = cv2.VideoCapture(idx)

        if cap.isOpened():
            return cap

    raise RuntimeError("No webcam found (checked indexes 0-2)")


def capture_image(save_dir="static/uploads"):

    """
    Capture image from webcam and save it.
    Press:
    c → capture
    q → quit
    """

    os.makedirs(save_dir, exist_ok=True)

    cap = open_camera()

    print("Press 'c' to capture image, 'q' to quit")

    path = None

    while True:

        ret, frame = cap.read()

        if not ret:
            continue

        cv2.imshow("FoodAI Camera", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):

            filename = f"capture_{int(time.time())}.jpg"

            path = os.path.join(save_dir, filename)

            cv2.imwrite(path, frame)

            print(f"Saved: {path}")

            break

        elif key == ord("q"):

            break

    cap.release()
    cv2.destroyAllWindows()

    return path
