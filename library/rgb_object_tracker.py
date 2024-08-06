import argparse
import configparser
import os

import cv2
import numpy as np

from library.Camera2Robot import cam_to_robot


class ColorNotFoundError(Exception):
    """Exception raised when a color is not found in the configuration."""


def load_color_ranges(config_file="library/color_config.ini"):
    """
    Load color ranges from a configuration file.

    Parameters:
        config_file (str): Path to the configuration file.

    Returns:
        dict: A dictionary with color ranges.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    color_ranges = {}
    for section in config.sections():
        ranges = {}
        for key, value in config.items(section):
            ranges[key] = np.array(list(map(int, value.split(","))))
        color_ranges[section] = ranges

    return color_ranges


def test_calibration(image, colors, color_ranges):
    """
    Test the calibration for the specified colors in the image.

    Parameters:
        image (ndarray): The image to test.
        colors (list): List of colors to test.
        color_ranges (dict): Color ranges configuration.
    """
    for color in colors:
        print("Testing color:", color)
        object_tracking(
            image,
            color,
            debug=True,
            debug_image_path=f"debug_{color}.png",
        )


def all_objects_are_visible(objects, image, debug=False):
    """
    Check if all objects are visible in the image.

    Parameters:
        objects (list): List of objects to check.
        image (ndarray): The image to check.
        color_ranges (dict): Color ranges configuration.
        debug (bool): Flag to enable debug mode.

    Returns:
        bool: True if all objects are visible, False otherwise.
    """

    for obj in objects:
        try:
            if object_tracking(image, obj, debug=debug) is None:
                if debug:
                    print("Block not found:", obj)
                return False
        except Exception as e:
            print("all_objects_are_visible: ", e)
            print(obj)
            raise Exception(e)
    return True


def get_object_pos(bottom_image, robot_idx, color, debug=False):
    """
    Get the position of an object in the image.

    Parameters:
        bottom_image (ndarray): The image to analyze.
        robot_idx (int): Robot index.
        color (str): Color of the object.
        color_ranges (dict): Color ranges configuration.
        debug (bool): Flag to enable debug mode.

    Returns:
        ndarray: The position of the object in robot coordinates.
    """
    cam_position = object_tracking(bottom_image, color, debug=debug)
    return cam_to_robot(robot_idx, cam_position)


def object_tracking(
    image,
    color,
    size_threshold=290,
    debug=False,
    debug_image_path="debug_image.png",
):
    """
    Track the object of a specified color in the image.

    Parameters:
        image (ndarray): The image to analyze.
        color (str): Color of the object to track.
        color_ranges (dict): Color ranges configuration.
        size_threshold (int): Minimum size of the object to track.
        debug (bool): Flag to enable debug mode.
        debug_image_path (str): Path to save the debug image.

    Returns:
        ndarray: The position of the object in the image.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    color_ranges = load_color_ranges()

    try:
        lower1, upper1, lower2, upper2 = get_color_ranges(color, color_ranges)
    except ColorNotFoundError as e:
        print("Object tracking: ", e)
        raise ColorNotFoundError(e)

    blurred = cv2.GaussianBlur(hsv, (5, 5), 0)
    mask1 = cv2.inRange(blurred, lower1, upper1)
    mask = mask1

    if lower2 is not None and upper2 is not None:
        mask2 = cv2.inRange(blurred, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

    mask = apply_morphological_operations(mask)
    large_contours = get_large_contours(mask, size_threshold)

    if not large_contours:
        if debug:
            print("No large contours found for color:", color)
        return None

    position = get_contour_center(large_contours, debug, color, image, debug_image_path)
    return position


def get_color_ranges(color, color_ranges):
    """
    Get the color ranges for a specified color.

    Parameters:
        color (str): The color to get ranges for.
        color_ranges (dict): Color ranges configuration.

    Returns:
        tuple: Lower and upper color ranges.

    Raises:
        ColorNotFoundError: If the color is not found in the configuration.
    """
    if color not in color_ranges:
        raise ColorNotFoundError(f"Color '{color}' not found in configuration.")
    ranges = color_ranges[color]
    return (
        ranges["lower1"],
        ranges["upper1"],
        ranges.get("lower2", None),
        ranges.get("upper2", None),
    )


def apply_morphological_operations(mask):
    """
    Apply morphological operations to the mask.

    Parameters:
        mask (ndarray): The mask to process.

    Returns:
        ndarray: The processed mask.
    """
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def get_large_contours(mask, size_threshold):
    """
    Get contours larger than the specified threshold.

    Parameters:
        mask (ndarray): The mask to find contours in.
        size_threshold (int): Minimum size of the contours.

    Returns:
        list: List of large contours.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) > size_threshold]

def get_contour_center(contours, debug, color, image, debug_image_path):
    """
    Get the center of the largest contour.

    Parameters:
        contours (list): List of contours.
        debug (bool): Flag to enable debug mode.
        color (str): Color of the object.
        image (ndarray): The image to analyze.
        debug_image_path (str): Path to save the debug image.

    Returns:
        ndarray: The position of the contour center.
    """
    largest_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest_contour)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    if debug:
        contour_area = cv2.contourArea(largest_contour)
        print("Largest contour for color:", color, "Area:", contour_area)
        if contour_area < 1000:
            print("No sufficiently large contours found")
            return None

        debug_object_tracker(image, largest_contour, contours, cx, cy, debug_image_path)

    return np.array([cx, cy])


def debug_object_tracker(image, largest_contour, contours, cx, cy, debug_image_path):
    """
    Debug the object tracker by saving an image with the detected contours.

    Parameters:
        image (ndarray): The image to debug.
        largest_contour (ndarray): The largest contour detected.
        contours (list): List of all contours detected.
        cx (int): X coordinate of the center.
        cy (int): Y coordinate of the center.
        debug_image_path (str): Path to save the debug image.
    """
    res = cv2.bitwise_and(
        image,
        image,
        mask=cv2.drawContours(
            np.zeros_like(image), [largest_contour], -1, 255, thickness=cv2.FILLED
        ),
    )
    cv2.circle(res, (cx, cy), 5, (0, 0, 255), -1)
    cv2.drawContours(res, contours, -1, (0, 255, 0), 2)
    cv2.imwrite(debug_image_path, res)


def main():
    """
    Main function to parse arguments and run the calibration test.
    """
    parser = argparse.ArgumentParser(description="Image color calibration checker")
    parser.add_argument("image_file", type=str, help="Path to the image file")
    parser.add_argument(
        "colors", type=str, nargs="+", help="List of colors to check in the image"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="color_config.ini",
        help="Path to the color ranges configuration file",
    )
    args = parser.parse_args()

    image_file = args.image_file
    colors = args.colors
    config_file = args.config

    if not os.path.isfile(image_file):
        print("The specified file does not exist")
        return

    image = cv2.imread(image_file)
    if image is None:
        print(f"Failed to load image: {image_file}")
        return

    color_ranges = load_color_ranges(config_file)

    print(f"Testing image: {image_file}")
    test_calibration(image, colors, color_ranges)


if __name__ == "__main__":
    main()
