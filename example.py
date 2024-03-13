from client.cloudgripper_client import GripperRobot
import time
import sys
import cv2
import os

# Get the CloudGripper API token from environment variables
token = os.environ['CLOUDGRIPPER_TOKEN']

# Create a GripperRobot instance
robotName = 'robot4'
robot = GripperRobot(robotName, token)

# Demonstrate various robot actions
img, timestamp = robot.getImage()
img, timestamp = robot.getImageTop()
robot.step_forward()
robot.step_backward()
robot.step_right()
robot.step_left()
robot.gripper_close()
robot.gripper_open()
robot.rotate(0)  # Rotate the robot to 0 degrees
robot.move_z(0.3)  # Move along the Z-axis to 0.3 position
robot.move_xy(0.5, 0.5)  # Move to X: 0.5, Y: 0.5
