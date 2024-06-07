# Import Essentials
import argparse
import os
import time

import cv2
import numpy as np

from client.cloudgripper_client import GripperRobot
from library.calibration import realCommandModification, sim2robot, undistort
from library.Camera2Robot import Camera2Robot
from library.object_tracking import object_tracking

"""
    This script is used to calibrate the position of the robot.
    00--01
    |    |
    10--11
    use the above as guide to calibrate the position of the robot, DONT use the move_xy number
"""


# Setup
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2OTgxNjQ0MywianRpIjoiYTRlZTU0YjQtMWRhYi00YjFiLTkxYzYtNzlkYzUzZTQ2MjNiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InphaGlkbXlAemFoaWQuY29tIiwibmJmIjoxNjY5ODE2NDQzfQ.q4Lx6rY8o0FVndCDSl6MaMV59EHWWb8Ng7Bxs5uGb84"

m, d = (
    [
        [505.24537524391866, 0.0, 324.5096286632362],
        [0.0, 505.6456651337437, 233.54118730278543],
        [0.0, 0.0, 1.0],
    ],
    [
        [-0.07727407195057368],
        [-0.047989733519315944],
        [0.12157420705123315],
        [-0.09667542135039282],
    ],
)

l_x, l_y = 38, 32


def calibrate(x: float, y: float, z: float, robot_idx):
    robot3 = GripperRobot(robot_idx, token)
    # new corner in pixel space
    # 0   60   75
    # 1  337   75
    # 2   60  406
    # 3  337  406

    # Note: commands are placed in a queue on the robot side. So the robot will no perform the next instruction until the previous execution is completed.
    # Note: Left, Right, Forward and Backward are with respect to the top camera, so the adjust for the bottom camera as required
    # Note: move_xy also follows the top camera. From the bottom camera 0,0 is on bottom right. From there 'x' increases going upwards and 'y' increases going left

    # Send commands
    # robot3.rotate(5)

    # robot3.gripper_open()
    #
    # robot3.gripper_close()  # close gripper
    # img, _ = robot3.getImageTop()
    # cv2.imwrite('./test/pick_red_top.jpg', img)

    # robot3.calibrate()
    # robot3.gripper_open()
    # robot3.gripper_close()
    # robot3.gripper_open():
    # print(robot3.get_state())
    # robot3.move_z(1)s
    robot3.move_z(z)
    # #
    # time.sleep(2.0)
    _, _ = robot3.getImage()
    target = np.array([x, y])
    ## target = realCommandModification(target)
    ## order = sim2robot(target)
    # order = target
    robot3.gripper_close()
    time.sleep(1)
    robot3.move_xy(x, y)
    # time.sleep(4.0)

    image, timestamp = robot3.getImage()  # Get bottom camera image
    undistort_img = undistort(image, m, d)
    # print(undistort_img.shape)
    # cv2.imwrite(os.path.join("/home/olivew/PycharmProjects/diffusion_policy/real_robot/visual_align", '4r.png'), undistort_img)
    # time.sleep(3.0)
    # robot3.move_xy(1, 0)
    # time.sleep(3.0)
    # robot3.move_xy(1, 1)
    # time.sleep(3.0)
    # robot3.move_xy(0, 1)
    # robot3.move_xy(1, 1)
    # robot3.move_xy(1, 0)
    # robot3.move_xy(0, 1)
    # robot3.move_xy(0, 0)

    # robot3.getImage()  # Get bottom camera image

    """
        array of length 5 :
        X position (normalized) - [0, 1]
        Y position (normalized) - [0, 1]
        Z position (normalized) - [0, 1]
        Rotation (deg) - [0 deg, 180 deg]
        Griper - [Open/0, Close/1]
    """

    while True:
        image, timestamp = robot3.getImage()  # Get bottom camera image
        undistort_img = undistort(image, m, d)
        # cropped_img = cropTopLeft(undistort_img, top_left_x=l_x, top_left_y=l_y)
        # cropped_img = cropCentral(cropped_img, rate=0.1)
        # print(cropped_img.shape)
        #  print(cropped_img)
        top, _ = robot3.getImageTop()
        # robot3.move_xy(0.8, 0.8)
        # robot3.move_xy(1, 1)
        # position = object_tracking(undistort_img)  # tracking the red object
        # robot_position = Camera2Robot(position, robot_idx)
        # print("robot_position", robot_position)
        # cv2.imshow('top', top)
        # print(undistort_img.shape)
        # cv2.imshow('top', image)

        # goal = [1,1]
        # movement = order2movement(goal[0], goal[1])
        # robot3.move_xy(movement[0], movement[1])
        # print(movement)
        # order = movement2order(movement[0], movement[1])
        # print(order)
        cv2.imshow("bottom", undistort_img)
        # cv2.imshow("top", top)
        # print(cropped_img.shape)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot_idx", type=str, help="Robot index")
    parser.add_argument("--x", type=float, help="X target")
    parser.add_argument("--y", type=float, help="Y target")
    parser.add_argument("--z", type=float, help="Z target")
    args = parser.parse_args()
    calibrate(args.x, args.y, args.z, args.robot_idx)
