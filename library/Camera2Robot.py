import cv2
# import cv2.aruco as aruco
import numpy as np

# the mapping relation
# Note: when fill the x and y, change the order of x and y
# e.g (robot_y, robot_x) - (pixel_y, pixel_x)
"""
    (0, 0) - (a1, b1)
    (0, 1) - (a2, b2)
    (1, 0) - (a3, b3)
    (1, 1) - (a4, b4)
"""

# Note: when calibrate, don't add the order2movement to move_x_y


robot_parameters = {
    "robot2": {
        "a1": 150,
        "b1": 69,
        "a2": 149,
        "b2": 441,
        "a3": 534,
        "b3": 67,
        "a4": 535,
        "b4": 435,
    },
    "robot3": {
        "a1": 52,
        "b1": 96,
        "a2": 53,
        "b2": 462,
        "a3": 402,
        "b3": 106,
        "a4": 401,
        "b4": 464,
    },
    "robot4": {
        "a1": 169,
        "b1": 49,
        "a2": 94,
        "b2": 530,
        "a3": 479,
        "b3": 162,
        "a4": 553,
        "b4": 429,
    },
    "robot5": {
        "a1": 187,
        "b1": 68,
        "a2": 186,
        "b2": 441,
        "a3": 580,
        "b3": 69,
        "a4": 578,
        "b4": 449,
    },
    "robot6": {  # not yet
        "a1": 108,
        "b1": 32,
        "a2": 119,
        "b2": 408,
        "a3": 499,
        "b3": 37,
        "a4": 501,
        "b4": 400,
    },
    "robotCR17": {
        "a1": 129,
        "b1": 74,
        "a2": 121,
        "b2": 464,
        "a3": 525,
        "b3": 81,
        "a4": 529,
        "b4": 464,
    },
    "robotCR18": {
        "a1": 138,
        "b1": 60,
        "a2": 133,
        "b2": 450,
        "a3": 541,
        "b3": 64,
        "a4": 537,
        "b4": 449,
    },
    "robotCR19": {
        "a1": 146,
        "b1": 80,
        "a2": 138,
        "b2": 459,
        "a3": 535,
        "b3": 86,
        "a4": 532,
        "b4": 461,
    },
    "robotCR20": {
        "a1": 144,
        "b1": 86,
        "a2": 137,
        "b2": 462,
        "a3": 539,
        "b3": 90,
        "a4": 532,
        "b4": 465,
    },
    "robotCR21": {
        "a1": 92,
        "b1": 84,
        "a2": 93,
        "b2": 479,
        "a3": 494,
        "b3": 89,
        "a4": 504,
        "b4": 466,
    },
    "robotCR22": {
        "a4": 556,
        "b4": 439,
        "a2": 152,
        "b2": 439,
        "a3": 556,
        "b3": 45,
        "a1": 147,
        "b1": 51,
    },
    "robot23": {
        "a1": 591,
        "b1": 29,

        "a3": 157,
        "b3": 26,

        "a2": 589,
        "b2": 463,

        "a4": 151,
        "b4": 466,
    },
}

# set robot frame as world frame



def Camera2Robot(cam_pos, robot_idx):
    if len(cam_pos) < 2:
        raise ValueError("Camera2Robot: Camera position must have at least 2 elements")

    if not robot_idx in robot_parameters:
        print("Robot index not found")
        return

    a1 = robot_parameters[robot_idx]["a1"]
    b1 = robot_parameters[robot_idx]["b1"]
    a2 = robot_parameters[robot_idx]["a2"]
    b2 = robot_parameters[robot_idx]["b2"]
    a3 = robot_parameters[robot_idx]["a3"]
    b3 = robot_parameters[robot_idx]["b3"]
    a4 = robot_parameters[robot_idx]["a4"]
    b4 = robot_parameters[robot_idx]["b4"]

    assert abs(b1 - b3) < 20, "Warning: b1 and b3 are not equal"
    assert abs(a1 - a2) < 20, "Warning: a1 and a2 are not equal"
    assert abs(b2 - b4) < 20, "Warning: b2 and b4 are not equal"
    assert abs(a3 - a4) < 20, "Warning: a3 and a4 are not equal"

    width = b2 - b1
    height = a1 - a3

    assert abs(width - height) < 70, "Warning: width and height are not equal"

    robot_x = (cam_pos[0] - a1) / height
    robot_y = (cam_pos[1] - b1) / width

    print("CAMERA2POS")
    print("x", robot_x)
    print("y", robot_y)

    if robot_x > 1.0:
        robot_x = 1.0
    if robot_y > 1.0:
        robot_y = 1.0

    robot_position = np.array([robot_x, robot_y])
    return robot_position


"""
def aruco_tracking(image):
    DEBUG = False
    positions = []
    # convert to grayscale
    # image = cv2.flip(image, 0)
    # image = cv2.flip(image, 1)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # initialize the detector parameters using default values
    parameters = aruco.DetectorParameters_create()
    # create dictionary
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    # detect the markers in the image
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=parameters
    )
    # if at least one marker detected
    print("len(corners)", len(corners))
    # print(rejectedImgPoints)

    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected AruCo corners
        for markerCorner, markerID in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            # compute the center (x, y)-coordinates of the ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            positions.append(np.array([cX, cY]))
            if DEBUG:
                # draw the ArUco detection on the image
                cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
                cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
    if DEBUG:
        # show the output image
        cv2.imshow("Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return np.array([cY, cX])
"""
