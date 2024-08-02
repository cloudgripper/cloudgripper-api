import argparse
import os

import cv2
import numpy as np


def test_calibration(image, colors):
    for color in colors:
        print("Testing color:", color)
        object_tracking(image, color, DEBUG=True, debug_image_path=f"debug_{color}.png")


def all_objects_are_visible(objects, image, DEBUG=False):
    for obj in objects:
        try:
            if object_tracking(image, obj, DEBUG=DEBUG) is None:
                if DEBUG:
                    print("block not found", obj)
                return False
        except Exception as e:  # TODO make custom exceptions
            print(e)
            print(obj)
            return False
    return True


def get_object_pos(robot_idx, color, debug=False):
    cam_position = object_tracking(bottom_image, color, DEBUG=debug)

    return cam_to_robot(robot_idx, cam_position)


def object_tracking(
    image,
    color="red",
    size_threshold=290,
    DEBUG=False,
    debug_image_path="debug_image.png",
):
    positions = []

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    colorFound = False

    # Define color ranges in HSV space
    if color == "red":
        colorFound = True

        # Two ranges to capture red colors in HSV
        lower1 = np.array([0, 50, 50])
        upper1 = np.array([10, 255, 255])

        lower2 = np.array([170, 50, 50])
        upper2 = np.array([180, 255, 255])

    elif color == "green":
        colorFound = True

        # Widened green spectrum, including darker greens
        lower1 = np.array([30, 40, 20])
        upper1 = np.array([90, 255, 255])

    elif color == "orange":
        colorFound = True

        lower1 = np.array([10, 100, 20])
        upper1 = np.array([25, 255, 255])

    if not colorFound:
        print("Color not found")
        return None

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(hsv, (5, 5), 0)

    mask1 = cv2.inRange(blurred, lower1, upper1)
    if color == "red":
        mask2 = cv2.inRange(blurred, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = mask1

    # Apply morphological operations to remove small noise
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Apply additional filtering based on contour area
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = [c for c in contours if cv2.contourArea(c) > size_threshold]

    # Create a new mask with large contours
    new_mask = np.zeros_like(mask)
    cv2.drawContours(new_mask, large_contours, -1, 255, thickness=cv2.FILLED)

    # Apply a second round of morphological operations
    mask = cv2.morphologyEx(new_mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    res = cv2.bitwise_and(image, image, mask=mask)

    if len(large_contours) > 0:
        c = max(large_contours, key=cv2.contourArea)
        M = cv2.moments(c)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        positions.append(np.array([cx, cy]))

        contour_area = cv2.contourArea(c)
        if DEBUG:
            print("largest contour for color:", color, contour_area)

        if contour_area < 1000:
            print("No sufficiently large contours found")
            return None

    else:
        if DEBUG:
            print("No large contours found of color", color)
        return None

    if DEBUG:
        print("debugging object tracker")
        cv2.circle(res, (cx, cy), 5, (0, 0, 255), -1)
        cv2.drawContours(res, large_contours, -1, (0, 255, 0), 2)

        # Save the debug image to a file
        cv2.imwrite(debug_image_path, res)

    return positions[0]


def main():
    parser = argparse.ArgumentParser(description="Image color calibration checker")
    parser.add_argument("image_file", type=str, help="Path to the image file")
    parser.add_argument(
        "colors", type=str, nargs="+", help="List of colors to check in the image"
    )
    args = parser.parse_args()

    image_file = args.image_file
    colors = args.colors

    # Check if file exists
    if not os.path.isfile(image_file):
        print("The specified file does not exist")
        return

    # Load the image
    image = cv2.imread(image_file)
    if image is None:
        print(f"Failed to load image: {image_file}")
        return

    print(f"Testing image: {image_file}")
    test_calibration(image, colors)


if __name__ == "__main__":
    main()
