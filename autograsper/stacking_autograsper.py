from grasper import AutograsperBase, RobotActivity
from library.rgb_object_tracker import (
    get_object_pos,
    all_objects_are_visible,
)
from library.utils import OrderType, pick_random_positions, get_undistorted_bottom_image
import numpy as np
import time
from typing import List, Tuple


class StackingAutograsper(AutograsperBase):
    def __init__(
        self,
        args,
        output_dir: str = "",
        colors=None,
        block_heights=None,
        position_bank=None,
        stack_position=None,
        object_size=2,
        camera_matrix=None,
        distortion_coefficients=None,
    ):
        super().__init__(args, output_dir, camera_matrix, distortion_coefficients)
        # Task-specific initialization
        self.colors = colors
        self.block_heights = block_heights
        self.position_bank = position_bank
        self.stack_position = stack_position
        self.object_size = object_size

        # Prepare experiment
        self.position_bank, self.stack_position = self.prepare_experiment(
            self.position_bank, self.stack_position
        )
        self.bottom_image = get_undistorted_bottom_image(
            self.robot, self.camera_matrix, self.distortion_coefficients
        )

    def prepare_experiment(self, position_bank, stack_position):
        if position_bank is None:
            position_bank = [[0.2, 0.2], [0.8, 0.2], [0.8, 0.2], [0.8, 0.8]]
        position_bank = np.array(position_bank)

        if stack_position is None:
            stack_position = [0.5, 0.5]

        return position_bank, stack_position

    def perform_task(self):
        # Implement task-specific code
        self.stack_objects(self.colors, self.block_heights, self.stack_position)


    def reset_task(self):
        # Implement task-specific reset
        random_reset_positions = pick_random_positions(
            self.position_bank, len(self.block_heights), self.object_size
        )
        self.reset_blocks(
            random_reset_positions,
            self.block_heights,
            stack_position=self.stack_position,
        )

    def stack_objects(self, colors, block_heights, stack_position):
        blocks = list(zip(colors, block_heights))
        bottom_color = colors[0]

        stack_height = 0

        for color, block_height in blocks:
            try:
                bottom_block_position = get_object_pos(
                    self.bottom_image, self.robot_idx, bottom_color
                )
                object_position = get_object_pos(
                    self.bottom_image, self.robot_idx, color, debug=True
                )
            except ValueError as e:
                print(f"Error finding object position for color '{color}': {e}")
                self.failed = True
                return  # Exit the function if an object is not found

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


    def reset_blocks(
        self,
        block_positions: List[List[float]],
        block_heights: np.ndarray,
        stack_position: List[float] = [0.5, 0.5],
        time_between_orders: float = 1.5,
    ):
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

    def pickup_and_place_object(
        self,
        object_position: Tuple[float, float],
        object_height: float,
        target_height: float,
        target_position: List[float] = [0.5, 0.5],
        time_between_orders: float = 1.5,
    ):
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
