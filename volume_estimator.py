import cv2
import numpy as np
import os


def estimate_volume(image_path, bbox=None, scale_factor=4500):
    """
    Estimate food volume from image.

    Parameters
    ----------
    image_path : str
        Path to image

    bbox : tuple or None
        YOLO bounding box (x1, y1, x2, y2)

    scale_factor : float
        Pixel area to volume conversion constant

    Returns
    -------
    float : estimated volume (cm3 approx)
    """

    if not os.path.exists(image_path):
        print(f"[❌] File not found: {image_path}")
        return 1.0

    image = cv2.imread(image_path)

    if image is None:
        print("[❌] Image loading failed")
        return 1.0

    try:

        # ---------------------------
        # Crop using YOLO bounding box
        # ---------------------------

        if bbox is not None:

            h, w = image.shape[:2]

            x1, y1, x2, y2 = map(int, bbox)

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            crop = image[y1:y2, x1:x2]

        else:

            crop = image

        if crop.size == 0:
            return 1.0

        # ---------------------------
        # Preprocessing
        # ---------------------------

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blur, 50, 150)

        # Morphology improves edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = cv2.erode(edges, kernel, iterations=1)

        # ---------------------------
        # Contour detection
        # ---------------------------

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return 1.0

        # ---------------------------
        # Largest contour = food
        # ---------------------------

        largest_contour = max(contours, key=cv2.contourArea)

        area = cv2.contourArea(largest_contour)

        if area < 100:
            return 1.0

        # ---------------------------
        # Pixel area → volume
        # ---------------------------

        volume = area / scale_factor

        volume = round(volume, 2)

        return max(volume, 0.1)

    except Exception as e:

        print(f"[ERROR] Volume estimation failed: {e}")

        return 1.0
