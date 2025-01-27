from grasper import AutograsperBase, RobotActivity
from library.rgb_object_tracker import (
    get_object_pos,
    all_objects_are_visible,
    test_calibration
)
from library.utils import OrderType, pick_random_positions, get_undistorted_bottom_image, clear_center, manual_control, run_calibration
import numpy as np
from typing import List, Tuple
import time
import random


class RandomGrasper(AutograsperBase):
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

        self.time_between_orders = 1

    def prepare_experiment(self, position_bank, stack_position):
        if position_bank is None:
            position_bank = [[0.2, 0.2], [0.8, 0.2], [0.8, 0.8]]
        position_bank = np.array(position_bank)

        if stack_position is None:
            stack_position = [0.5, 0.5]

        return position_bank, stack_position
    
    def move_red_to_center(self):
 
        target_color = "red"
        object_position = get_object_pos(
            self.bottom_image, self.robot_idx, target_color)
        self.pickup_and_place_object(
            object_position,
            0,
            0,
            target_position=[0.5,0.5]
        )


    def perform_task(self):

        
        # run_calibration(0.2, self.robot)
        

        # test_calibration(self.bottom_image, ["red"])
        # self.robot.gripper_open()

        # manual_control(self.robot)
        # self.move_red_to_center()

        margin = 0.2
        # random_position = self.generate_new_block_position()
        random_position = [0,0]

        d_x = np.random.uniform(-0.08,0.08)
        d_y = np.random.uniform(-0.08,0.08)

        object_position = get_object_pos(
            self.bottom_image, self.robot_idx, "green", debug=True)
        
        random_position[0] = object_position[0] + d_x
        random_position[1] = object_position[1] + d_y

        x = random_position[0]
        y = random_position[1]



        self.queue_robot_orders([
            (OrderType.MOVE_XY, random_position),
            (OrderType.GRIPPER_OPEN, []),
            (OrderType.MOVE_Z, [0]),
            (OrderType.GRIPPER_CLOSE, [])], delay=4.0
        )


        object_position = get_object_pos(
            self.bottom_image, self.robot_idx, "green", debug=True)
        if (
            # abs(x - 0.5) > margin
            # and abs(y - 0.5) > margin
            # and np.linalg.norm(np.array(random_position) - np.array(object_position)) < 0.12
            np.linalg.norm(np.array(random_position) - np.array(object_position)) < 0.12
        ):
            self.failed = False
            print("succesful grasp")
        else:
            print("failed grasp")
            self.failed = True

        print("task complete")

    def generate_new_block_position(self):
        import random

        margin = 0.25
        while True:
            x = random.uniform(0.2, 0.8)
            y = random.uniform(0.2, 0.8)
            avoid_position = [0.5, 0.5]
            dist = np.sqrt( np.pow(x - avoid_position[0], 2) + np.pow(y-avoid_position[1], 2) )

            if dist > margin:
                break

        return [x, y]

    def recover_after_fail(self):

        self.robot.gripper_open()
        time.sleep(0.5)
        self.go_to_start()
    
    def _reset_target_block(self):

        block_pos = self.generate_new_block_position()

        target_color = "green"
        object_position = get_object_pos(
            self.bottom_image, self.robot_idx, target_color)
        self.pickup_and_place_object(
            object_position,
            0,
            0,
            target_position=block_pos,
        )

        margin = 0.1
        red_position = get_object_pos(
            self.bottom_image, self.robot_idx, "red", debug=False)

        if abs(red_position[0] - 0.5) > margin and abs(red_position[1] - 0.5) > margin:
            self.move_red_to_center()


    def reset_task(self):

        self._reset_target_block()
        self.go_to_start

        return

    def pickup_and_place_object(
        self,
        object_position: Tuple[float, float],
        object_height: float,
        target_height: float,
        target_position: List[float] = [0.5, 0.5],
        time_between_orders: float = 2.0,
    ):
        orders = [
            (OrderType.GRIPPER_OPEN, []),
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, object_position),
            #(OrderType.GRIPPER_OPEN, []),
            (OrderType.MOVE_Z, [object_height]),
            (OrderType.GRIPPER_CLOSE, []),
            (OrderType.MOVE_Z, [1]),
            (OrderType.MOVE_XY, target_position),
            (OrderType.MOVE_Z, [target_height]),
            (OrderType.GRIPPER_OPEN, []),
        ]
        self.queue_robot_orders(orders, time_between_orders)

    def call_real_eval(self):
        import subprocess

        # Define the arguments from the bash command
        args = [
            "python", "real_eval.py",
            "exp_name=moco_vit_small",
            "data_name=RM",
            "agent=vit_small",
            "agent.features.restore_path=/workspaces/CloudGripper_Stack_1k/assets/pre_trained_weights/moco_resnet18/checkpoint.pth.tar",
            "checkpoint_path=/workspaces/CloudGripper_Stack_1k/assets/Policy/moco_resnet18/checkpoint_0.pth",
            "agent.features.model_type=moco",
            "devices=1",
            "wandb.name=moco_vit_small_RM"
        ]

        # Run the command
        try:
            result = subprocess.run(args, check=True)
            print("Real-world evaluation completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")




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
                    self.bottom_image, self.robot_idx, color, debug=False
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