from abc import ABC, abstractmethod
import os
import sys
import time
from enum import Enum
from typing import List, Tuple

import numpy as np
from dotenv import load_dotenv

# Ensure the project root is in the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import project-specific modules
from client.cloudgripper_client import GripperRobot
from library.utils import OrderType, queue_orders, clear_center

# Load environment variables
load_dotenv()


class RobotActivity(Enum):
    ACTIVE = 1
    RESETTING = 2
    FINISHED = 3
    STARTUP = 4


class AutograsperBase(ABC):
    def __init__(
        self,
        args,
        output_dir: str = "",
        camera_matrix=None,
        distortion_coefficients=None,
    ):
        self.token = os.getenv("ROBOT_TOKEN")
        if not self.token:
            raise ValueError("ROBOT_TOKEN environment variable not set")

        self.output_dir = output_dir
        self.start_time = time.time()
        self.failed = False

        # Camera calibration parameters
        if camera_matrix is None or distortion_coefficients is None:
            raise ValueError("Camera calibration parameters must be provided")
        self.camera_matrix = camera_matrix
        self.distortion_coefficients = distortion_coefficients

        self.state = RobotActivity.STARTUP
        self.start_flag = False

        self.robot = self.initialize_robot(args.robot_idx, self.token)
        self.robot_idx = args.robot_idx

    @staticmethod
    def initialize_robot(robot_idx: int, token: str) -> GripperRobot:
        try:
            return GripperRobot(robot_idx, token)
        except Exception as e:
            raise ValueError("Invalid robot ID or token") from e

    def queue_robot_orders(self, orders: List[Tuple[OrderType, List]], delay: float=1):
        queue_orders(self.robot, orders, delay, output_dir=self.output_dir)

    def startup(self, position: List[float]):
        self.robot.rotate(0)
        time.sleep(0.5)
        startup_commands = [
            (OrderType.GRIPPER_OPEN, []),
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, position),
        ]
        self.queue_robot_orders(startup_commands, 1)
        time.sleep(2)

    def recover_after_fail(self):
        clear_center(self.robot)

    def wait_for_start_signal(self):
        while not self.start_flag:
            time.sleep(0.1)

    def go_to_start(self):
        positions = [[1, 0.7], [0, 0.7]]
        positions = np.array(positions)
        position = positions[1]
        orders = [
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, position),
        ]
        self.queue_robot_orders(orders, 1)
        self.robot.gripper_close()

    def run_grasping(self):
        while self.state != RobotActivity.FINISHED:
            self.go_to_start()
            self.state = RobotActivity.ACTIVE

            self.wait_for_start_signal()
            self.start_flag = False

            # Call task-specific method
            try:
                self.perform_task()
            except ValueError as e:
                print(f"Error during perform_task: {e}")
                self.failed = True
            except Exception as e:
                print(f"Unexpected error during perform_task: {e}")
                raise

            time.sleep(2)
            self.state = RobotActivity.RESETTING
            time.sleep(2)

            if self.failed:
                print("Experiment failed, recovering")
                self.recover_after_fail()
                self.failed = False
            else:
                self.reset_task()

            self.state = RobotActivity.STARTUP


    @abstractmethod
    def perform_task(self):
        pass

    @abstractmethod
    def reset_task(self):
        pass
