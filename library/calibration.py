import cv2
import numpy as np

from library.bottom_image_preprocessing import rotate


def calibrate_fisheye(images, pattern_size, square_size):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    obj_points = []  # 3D points in real world space
    img_points = []  # 2D points in image plane

    objp = np.zeros((1, pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[0, :, :2] = (
        np.mgrid[0 : pattern_size[0], 0 : pattern_size[1]].T.reshape(-1, 2)
        * square_size
    )

    for img in images:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

        if ret:
            obj_points.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            img_points.append(corners2)

    ret, mtx, dist, rvecs, tvecs = cv2.fisheye.calibrate(
        obj_points, img_points, gray.shape[::-1], None, None
    )
    return ret, mtx, dist, rvecs, tvecs


def undistort_fisheye(img_path, mtx, dist):
    # image = cv2.imread(img_path)
    image = img_path
    mtx, dist = np.array(mtx), np.array(dist)
    h, w = image.shape[:2]
    new_mtx, roi = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        mtx, dist, (w, h), None
    )
    mapx, mapy = cv2.fisheye.initUndistortRectifyMap(
        mtx, dist, np.eye(3), new_mtx, (w, h), cv2.CV_16SC2
    )
    undistorted_image = cv2.remap(
        image,
        mapx,
        mapy,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
    )
    x, y, w, h = roi
    undistorted_image = undistorted_image[y : y + h, x : x + w]
    return undistorted_image


def undistort(img_path, K, D):
    # img = cv2.imread(img_path)
    img = img_path
    K, D = np.array(K), np.array(D)
    h, w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), K, img.shape[:2][::-1], cv2.CV_16SC2
    )
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT
    )
    # undistorted_img = cv2.flip(undistorted_img, 1)
    undistorted_img = cv2.flip(undistorted_img, 0)
    undistorted_img = rotate(undistorted_img, 90)
    return undistorted_img


# order to robot movement
def order2movement(x, y, center=np.array([0.5, 0.5])):
    point = np.array([x, y])
    # Translate the origin to the center point
    translated = point - center

    # Perform the rotation by 180 degrees
    rotated = np.array([[-1, 0], [0, -1]]) @ translated

    # Translate the origin back to (0, 0)
    final_point = rotated + center

    return final_point[::-1]


def movement2order(x, y, center=np.array([0.5, 0.5])):
    point = np.array([x, y])
    # Translate the origin to the center point
    translated = point - center

    # Perform the rotation by 180 degrees
    rotated = np.array([[-1, 0], [0, -1]]) @ translated

    # Translate the origin back to (0, 0)
    final_point = rotated + center

    return final_point[::-1]


def cropTopLeft(image_array, top_left_x, top_left_y):
    # array in dimension (y, x, 3)
    cropped_image_array = image_array[top_left_y:, top_left_x:]
    return cropped_image_array


def cropCentral(image_array, rate=0.05):
    # array in dimension (y, x, 3)
    y, x = image_array.shape[:2]
    pixel_y, pixel_x = int(y * rate), int(x * rate)
    y_start, y_end, x_start, x_end = pixel_y, y - pixel_y, pixel_x, x - pixel_x
    cropped_image_array = image_array[y_start:y_end, x_start:x_end]
    return cropped_image_array


def sim2robot(point, center=np.array([0.5, 0.5])):
    """
    Simulation coordinate:
    (0, 0) - (1, 0)
    (0, 1) - (1, 1)

    Real robot coordinate: (command coordinate)
    (1, 1) - (0, 1)
    (1, 0) - (0, 0)

    Rotate for 180 centering in [0.5, 0.5]
    """
    point = np.array(point)
    # Translate the origin to the center point
    translated = point - center

    # Perform the rotation by 180 degrees
    rotated = np.array([[-1, 0], [0, -1]]) @ translated

    # Translate the origin back to (0, 0)
    final_point = rotated + center

    return final_point


def realCommandModification(
    coord, new_min_x=0.18, new_max_x=0.86, new_min_y=0.09, new_max_y=0.89
):
    """--> x
        |
        |
        y
    (0, 0) ---- (480, 0)              (80, 100) ---- (450, 100)
      |            |                     |            |
      |            |        -->          |            |
      |            |                     |            |
    (0, 640) -- (480, 640)           (80, 540) --- (450, 540)
    """
    x, y = coord[0], coord[1]
    # Calculate the ratios
    new_x = new_min_x + x * (new_max_x - new_min_x)
    new_y = new_min_y + y * (new_max_y - new_min_y)

    return new_x, new_y
