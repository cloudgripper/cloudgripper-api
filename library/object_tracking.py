import cv2
import numpy as np

# write an object tracking function, using rgb color space


def test_calibration(image, colors):
    for color in colors:
        print("Testing color: ", color)
        object_tracking(image, color, DEBUG=True)


def object_tracking(image, color="red", size_threshold=150, DEBUG=False):
    positions = []

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    colorFound = False

    # the first bounds are for the lower range of the color
    # the second bounds are for the upper range of the color

    # to find the bounds of the color, use the hsv_color_picker.py script

    if color == "red":
        colorFound = True

        lower1 = np.array([0, 100, 100])
        upper1 = np.array([10, 255, 255])

        lower2 = np.array([160, 100, 100])
        upper2 = np.array([179, 255, 255])

    if color == "green":
        colorFound = True

        lower1 = np.array([62, 170, 11])
        upper1 = np.array([82, 190, 91])

        lower2 = np.array([64, 94, 0])
        upper2 = np.array([84, 114, 0])

    if color == "orange":
        colorFound = True

        lower1 = np.array([0, 193, 67])
        upper1 = np.array([0, 213, 147])

        lower2 = np.array([0, 166, 170])
        upper2 = np.array([0, 186, 250])

    # TODO add orange

    if not colorFound:
        print("Color not found")
        return None

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)

    mask = cv2.bitwise_or(mask1, mask2)
    res = cv2.bitwise_and(image, image, mask=mask)
    # find contours in the binary image
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # find the biggest contour (c) by the area
    if len(contours) > 0:
        large_contours = [c for c in contours if cv2.contourArea(c) > size_threshold]
        if len(large_contours) > 0:
            c = max(large_contours, key=cv2.contourArea)
            # find the center of the biggest contour
            M = cv2.moments(c)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            positions.append(np.array([cx, cy]))
    else:
        print("No contours found")
        return None

        if DEBUG:
            # draw the center of the circle
            cv2.circle(res, (cx, cy), 5, (0, 0, 255), -1)
            # draw the contour of the circle
            cv2.drawContours(res, contours, -1, (0, 255, 0), 2)
    if DEBUG:
        # cv2.imshow('mask', mask)
        window_name = "res " + color
        cv2.imshow(window_name, res)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return np.array([cy, cx])
