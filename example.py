from client.cloudgripper_client import GripperRobot
import time
import sys
import cv2
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Get the CloudGripper API token from environment variables
token = os.getenv("CLOUDGRIPPER_TOKEN")

# Create a GripperRobot instance
robotName = "robot23"
robot = GripperRobot(robotName, token)

# Function to display multiple images using OpenCV


def display_images(images, window_name="Robot Images"):
    # Get dimensions of the first image
    height, width = images[0].shape[:2]

    # Resize all images to the same dimensions
    resized_images = [cv2.resize(image, (width, height)) for image in images]

    # Concatenate images horizontally
    concatenated_image = np.concatenate(resized_images, axis=1)

    # Display the image
    cv2.imshow(window_name, concatenated_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# List to store images for display
images = []

# Get initial images
img_base, timestamp = robot.getImageBase()
img_top, timestamp = robot.getImageTop()

# Convert images to proper format and append to list
images.append(cv2.cvtColor(np.array(img_base), cv2.COLOR_RGB2BGR))
images.append(cv2.cvtColor(np.array(img_top), cv2.COLOR_RGB2BGR))

# Perform various robot actions and capture images
actions = [
    ("move_xy_0.5_0.5", lambda: robot.move_xy(1.0, 0.0)),
    ("gripper_close", robot.gripper_close),
    ("rotate_0", lambda: robot.rotate(0)),
    ("move_z_0.3", lambda: robot.move_z(0.3)),
    ("move_xy_0.5_0.5", lambda: robot.move_xy(0.5, 0.5)),
    ("gripper_open", robot.gripper_open),
]

# Execute actions and capture images after each action
for action_name, action in actions:
    action()  # Perform the action
    time.sleep(1)  # Wait a bit for the action to complete
    img_base, timestamp = robot.getImageBase()  # Get new image from base camera
    images.append(cv2.cvtColor(np.array(img_base), cv2.COLOR_RGB2BGR))

# Display all images
display_images(images)
