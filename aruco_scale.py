# utils/aruco_scale.py

import cv2
import numpy as np


def cm_per_pixel_with_aruco(image_bgr, marker_len_cm=5.0):

    try:

        aruco = cv2.aruco

    except AttributeError:

        print("OpenCV ArUco module not installed.")
        return None


    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    parameters = aruco.DetectorParameters_create()

    corners, ids, _ = aruco.detectMarkers(
        image_bgr,
        dictionary,
        parameters=parameters
    )

    if ids is None or len(corners) == 0:

        return None


    marker = corners[0][0]

    side_px = np.linalg.norm(marker[0] - marker[1])

    if side_px < 1e-3:

        return None


    cm_per_px = marker_len_cm / side_px

    return cm_per_px
