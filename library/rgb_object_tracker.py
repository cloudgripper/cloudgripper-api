import cv2
import numpy as np


def test_calibration(image, colors):
    for color in colors:
        print("Testing color:", color)
        object_tracking(image, color, DEBUG=True)

def all_objects_are_visible(blocks, image):
    for block in blocks:
        try:
            if object_tracking(image, block[0]) is None:
                print("block not found")
                return False

        except Exception:  # TODO make custom exceptions
            return False

    return True

def object_tracking(image, color="red", size_threshold=290, DEBUG=False):
    positions = []

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    colorFound = False

    # Define color ranges in RGB space
    if color == "red":
        colorFound = True

        lower1 = np.array([0, 0, 100])
        upper1 = np.array([100, 100, 255])

        lower2 = np.array([160, 0, 0])
        upper2 = np.array([255, 100, 100])

    if color == "green":
        colorFound = True

        lower1 = np.array([9, 22, 15])
        upper1 = np.array([29, 42, 35])

        lower2 = np.array([10, 31, 24])
        upper2 = np.array([30, 51, 44])

    if color == "orange":
        colorFound = True

        lower1 = np.array([132, 29, 10])
        upper1 = np.array([152, 49, 30])

        lower2 = np.array([95, 23, 11])
        upper2 = np.array([115, 43, 31])

    if not colorFound:
        print("Color not found")
        return None

    mask1 = cv2.inRange(rgb, lower1, upper1)
    mask2 = cv2.inRange(rgb, lower2, upper2)

    mask = cv2.bitwise_or(mask1, mask2)
    res = cv2.bitwise_and(image, image, mask=mask)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        large_contours = [c for c in contours if cv2.contourArea(c) > size_threshold]
        if len(large_contours) > 0:
            c = max(large_contours, key=cv2.contourArea)
            M = cv2.moments(c)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            positions.append(np.array([cx, cy]))
    else:
        print("No contours found")
        return None

    if DEBUG:
        cv2.circle(res, (cx, cy), 5, (0, 0, 255), -1)
        cv2.drawContours(res, contours, -1, (0, 255, 0), 2)

        window_name = "res " + color
        cv2.imshow(window_name, res)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return np.array([cy, cx])
