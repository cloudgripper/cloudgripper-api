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
                print("block not found", block)
                return False

        except Exception as e:  # TODO make custom exceptions
            print(e)
            print(block)
            return False

    return True


def object_tracking(
    image,
    color="red",
    size_threshold=290,
    DEBUG=False,
    debug_image_path="debug_image.png",
):
    positions = []

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    colorFound = False

    # Define color ranges in RGB space
    if color == "red":
        colorFound = True

        # Adjusted color range to include more brownish reds
        lower1 = np.array(
            [0, 0, 100]
        )  # Higher blue value to start including lighter browns
        upper1 = np.array(
            [100, 90, 240]
        )  # Increased red and slightly increased green/blue

        lower2 = np.array([160, 0, 0])  # Higher starting red for darker browns
        upper2 = np.array(
            [230, 110, 100]
        )  # Extended range to include more of the brown spectrum

    elif color == "green":
        colorFound = True

        lower1 = np.array([9, 22, 15])
        upper1 = np.array([29, 42, 35])

        lower2 = np.array([10, 31, 24])
        upper2 = np.array([30, 51, 44])

    elif color == "orange":
        colorFound = True

        # More inclusive ranges for orange
        lower1 = np.array([125, 20, 0])
        upper1 = np.array([185, 75, 55])

        lower2 = np.array([195, 55, 15])
        upper2 = np.array([255, 125, 75])

    if not colorFound:
        print("Color not found")
        return None

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(rgb, (5, 5), 0)

    mask1 = cv2.inRange(blurred, lower1, upper1)
    mask2 = cv2.inRange(blurred, lower2, upper2)

    mask = cv2.bitwise_or(mask1, mask2)

    # Apply morphological operations to remove small noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

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
        print("debugging object tracker")
        cv2.circle(res, (cx, cy), 5, (0, 0, 255), -1)
        cv2.drawContours(res, contours, -1, (0, 255, 0), 2)

        # Save the debug image to a file
        cv2.imwrite(debug_image_path, res)

    return positions[0]
