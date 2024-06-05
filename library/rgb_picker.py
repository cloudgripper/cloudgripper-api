import sys
import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np

image_rgb = None
pixel = (0, 0, 0)  # RANDOM DEFAULT VALUE
ftypes = [
    ("JPG", "*.jpg;*.JPG;*.JPEG"),
    ("PNG", "*.png;*.PNG"),
    ("GIF", "*.gif;*.GIF"),
    ("All files", "*.*"),
]


def check_boundaries(value, tolerance):
    """
    Adjusts RGB values to stay within valid range (0-255).
    """
    value = max(0, min(255, value + tolerance))
    return value


def pick_color(event, x, y, flags, param):
    global image_rgb
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_rgb[y, x]
        # Red, Green, and Blue values directly from the pixel
        red_upper = check_boundaries(pixel[0], 10)
        red_lower = check_boundaries(pixel[0], -10)
        green_upper = check_boundaries(pixel[1], 10)
        green_lower = check_boundaries(pixel[1], -10)
        blue_upper = check_boundaries(pixel[2], 10)
        blue_lower = check_boundaries(pixel[2], -10)
        upper = np.array([red_upper, green_upper, blue_upper])
        lower = np.array([red_lower, green_lower, blue_lower])
        print(lower, upper)


def main():
    global image_rgb
    root = tk.Tk()
    root.withdraw()  # HIDE THE TKINTER GUI
    file_path = filedialog.askopenfilename(filetypes=ftypes)
    root.update()
    image_src = cv2.imread(file_path)
    cv2.imshow("BGR", image_src)
    # Convert BGR image to RGB directly
    image_rgb = cv2.cvtColor(image_src, cv2.COLOR_BGR2RGB)
    cv2.imshow("RGB", image_rgb)
    # Set up callback for picking colors
    cv2.setMouseCallback("RGB", pick_color)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
