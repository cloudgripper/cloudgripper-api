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
from library.rgb_object_tracker import all_objects_are_visible, get_object_pos
from library.utils import (OrderType, get_undistorted_bottom_image,
                           pick_random_positions, queue_orders, clear_center)

# Load environment variables
load_dotenv()


class RobotActivity(Enum):
    ACTIVE = 1
    RESETTING = 2
    FINISHED = 3
    STARTUP = 4


class Autograsper:
    def __init__(self, args, output_dir: str = ""):
        """
        Initialize the Autograsper with the provided arguments.

        :param args: Command-line arguments
        :param output_dir: Directory to save state data
        """
        self.token = os.getenv("ROBOT_TOKEN")
        if not self.token:
            raise ValueError("ROBOT_TOKEN environment variable not set")

        self.output_dir = output_dir
        self.start_time = time.time()
        self.failed = False

        # Camera calibration parameters
        self.m = np.array(
            [
                [505.24537524391866, 0.0, 324.5096286632362],
                [0.0, 505.6456651337437, 233.54118730278543],
                [0.0, 0.0, 1.0],
            ]
        )
        self.d = np.array(
            [
                -0.07727407195057368,
                -0.047989733519315944,
                0.12157420705123315,
                -0.09667542135039282,
            ]
        )

        self.state = RobotActivity.STARTUP
        self.start_flag = False

        self.robot = self.initialize_robot(args.robot_idx, self.token)
        self.robot_idx = args.robot_idx
        self.bottom_image = get_undistorted_bottom_image(self.robot, self.m, self.d)

    @staticmethod
    def initialize_robot(robot_idx: int, token: str) -> GripperRobot:
        """
        Initialize the GripperRobot instance.

        :param robot_idx: Index of the robot.
        :param token: Authentication token for the robot.
        :return: GripperRobot instance.
        """
        try:
            return GripperRobot(robot_idx, token)
        except Exception as e:
            raise ValueError("Invalid robot ID or token") from e

    def queue_robot_orders(self, orders: List[Tuple[OrderType, List]], delay: float):
        """
        Queue a list of orders to the robot.

        :param orders: List of orders to queue.
        :param delay: Time delay between orders.
        """
        queue_orders(self.robot, orders, delay, output_dir=self.output_dir)

    def pickup_and_place_object(
        self,
        object_position: Tuple[float, float],
        object_height: float,
        target_height: float,
        target_position: List[float] = [0.5, 0.5],
        time_between_orders: float = 1.5,
    ):
        """
        Pickup and place an object from one position to another.

        :param object_position: Position of the object to pick up.
        :param object_height: Height of the object.
        :param target_height: Target height for placing the object.
        :param target_position: Target position for placing the object.
        :param time_between_orders: Time to wait between orders.
        """
        orders = [
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, object_position),
            (OrderType.GRIPPER_OPEN, []),
            (OrderType.MOVE_Z, [object_height]),
            (OrderType.GRIPPER_CLOSE, []),
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, target_position),
            (OrderType.MOVE_Z, [target_height]),
            (OrderType.GRIPPER_OPEN, []),
        ]
        self.queue_robot_orders(orders, time_between_orders)

    def reset(
        self,
        block_positions: List[List[float]],
        block_heights: np.ndarray,
        stack_position: List[float] = [0.5, 0.5],
        time_between_orders: float = 1.5,
    ):
        """
        Reset the blocks to their initial positions.

        :param block_positions: Positions of the blocks.
        :param block_heights: Heights of the blocks.
        :param stack_position: Position for stacking the blocks.
        :param time_between_orders: Time to wait between orders.
        """
        rev_heights = np.flip(block_heights.copy())
        target_z = sum(rev_heights)

        for index, block_pos in enumerate(block_positions):
            target_z -= rev_heights[index]
            orders = []

            if index == 0:
                orders += [
                    (OrderType.MOVE_Z, [1]),
                    (OrderType.MOVE_XY, stack_position),
                    (OrderType.GRIPPER_OPEN, []),
                ]

            orders += [
                (OrderType.MOVE_Z, [target_z]),
                (OrderType.GRIPPER_CLOSE, []),
                (OrderType.MOVE_Z, [1]),
                (OrderType.MOVE_XY, block_pos),
                (OrderType.MOVE_Z, [0]),
                (OrderType.GRIPPER_OPEN, []),
            ]

            if index != len(rev_heights) - 1:
                orders += [
                    (OrderType.MOVE_Z, [target_z]),
                    (OrderType.MOVE_XY, stack_position),
                ]

            self.queue_robot_orders(orders, time_between_orders)

    def startup(self, position: List[float]):
        """
        Perform startup sequence at a given position.

        :param position: Position to start up at.
        """
        self.robot.rotate(0)
        time.sleep(0.5)
        startup_commands = [
            (OrderType.GRIPPER_OPEN, []),
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, position),
        ]
        self.queue_robot_orders(startup_commands, 1)
        time.sleep(1)

    def recover_after_fail(self):
        clear_center(self.robot)

    def wait_for_start_signal(self):
        """
        Wait for the start signal.
        """
        while not self.start_flag:
            print("Waiting for start signal")
            time.sleep(0.1)

    def prepare_experiment(self, position_bank, stack_position):
        """
        Prepare the experiment by setting default positions.

        :param position_bank: List of start positions for blocks.
        :param stack_position: Position to stack the blocks.
        :return: Tuple containing position_bank and stack_position.
        """
        if position_bank is None:
            position_bank = [[0.2, 0.2], [0.8, 0.2], [0.8, 0.2], [0.8, 0.8]]
        position_bank = np.array(position_bank)

        if stack_position is None:
            stack_position = [0.5, 0.5]

        return position_bank, stack_position

    def stack_objects(self, colors, block_heights, stack_position):
        """
        Stack objects based on their colors and heights.

        :param colors: List of colors for the blocks.
        :param block_heights: List of heights corresponding to each block.
        :param stack_position: Position to stack the blocks.
        """
        blocks = list(zip(colors, block_heights))
        bottom_color = colors[0]

        stack_height = 0

        for color, block_height in blocks:

            bottom_block_position = get_object_pos(
                self.bottom_image, self.robot_idx, bottom_color
            )
            object_position = get_object_pos(
                self.bottom_image, self.robot_idx, color, debug=True
            )

            target_pos = (
                bottom_block_position if color != bottom_color else stack_position
            )

            self.pickup_and_place_object(
                object_position,
                max(block_height - 0.20, 0.02),
                stack_height,
                target_position=target_pos,
            )

            stack_height += block_height

    def run_grasping(
        self,
        colors,
        block_heights,
        position_bank=None,
        stack_position=None,
        object_size: float = 2,
    ):
        """
        Run the main grasping loop.

        :param colors: List of colors for the blocks.
        :param block_heights: List of heights corresponding to each block.
        :param position_bank: List of start positions for blocks. Defaults to predefined positions.
        :param stack_position: Position to stack the blocks. Defaults to [0.5, 0.5].
        :param object_size: Size of the objects.
        """
        position_bank, stack_position = self.prepare_experiment(
            position_bank, stack_position
        )

        if not all_objects_are_visible(colors, self.bottom_image):
            print("All blocks not visible")

        while self.state is not RobotActivity.FINISHED:
            try:
                self.go_to_start()
                self.state = RobotActivity.ACTIVE

                self.wait_for_start_signal()
                self.start_flag = False

                # self.stack_objects(colors, block_heights, stack_position)
                self.robot.move_xy(0.5, 0.5)
                time.sleep(1)
                self.robot.move_xy(0.9, 0.2)
                time.sleep(1)
                self.robot.move_xy(0.1, 0.5)
                time.sleep(2)

                self.go_to_start()
                time.sleep(1)
                self.state = RobotActivity.RESETTING
                time.sleep(1)

                if self.failed:
                    print("Experiment failed, recovering")
                    self.recover_after_fail()
                    self.failed = False
                else:
                    random_reset_positions = pick_random_positions(
                        position_bank, len(block_heights), object_size
                    )
                    self.reset(
                        random_reset_positions,
                        block_heights,
                        stack_position=stack_position,
                    )
                    self.go_to_start()

                self.state = RobotActivity.STARTUP

            except Exception as e:
                print(
                    f"Run grasping loop: An exception of type {type(e).__name__} occurred. Arguments: {e.args}"
                )
                raise Exception("Autograsping failed")

    def go_to_start(self):
        """
        Move the robot to the start position.
        """
        positions = [[1, 0.7], [0, 0.7]]
        positions = np.array(positions)

        position = np.choose(1, positions)

        orders = [
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, position),
        ]
        self.queue_robot_orders(orders, 2)
