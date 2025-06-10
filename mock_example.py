from client.cloudgripper_client_mock import GripperRobotMock
import time
import sys
import cv2
import os

# Get the CloudGripper API token from environment variables
token = os.environ.get('CLOUDGRIPPER_TOKEN', 'mock-token')

# Create a GripperRobot instance
robotName = 'robot6'
robot = GripperRobotMock(robotName, token)

robot.failier_rate = 0.01 # 1% probability of command failure

# Demonstrate various robot actions
print(robot.get_state())
robot.move_xy(0.5, 0.5)
robot.move_z(0.8)
robot.rotate(0)
robot.gripper_open()


img_base, timestamp = robot.getImageBase()
img_top, timestamp = robot.getImageTop()
# 
if img_base is not None:
    print(img_base.shape)
if img_top is not None:
    print(img_top.shape)