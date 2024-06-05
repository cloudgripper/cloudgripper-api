import time
import json
from enum import Enum
from typing import List, Optional, Tuple
import os
import numpy as np

from client.cloudgripper_client import GripperRobot
from library.calibration import undistort


class OrderType(Enum):
    MOVE_XY = 1
    MOVE_Z = 2
    GRIPPER_CLOSE = 3
    GRIPPER_OPEN = 4


def save_state(robot: GripperRobot, output_dir: str, start_time: float, previous_order: Optional[Tuple[OrderType, List[float]]] = None):
    """
    Save the current state of the robot to the states.json file.

    :param robot: The robot to get the state from
    :param output_dir: Directory to save state data
    :param start_time: The start time of the autograsper process
    :param previous_order: The previous order executed by the robot
    """
    state, timestamp = robot.get_state()
    relative_time = timestamp - start_time

    if previous_order is not None:
        order_type, order_value = previous_order
        state["previous_order"] = {
            "order_type": order_type.name,
            "order_value": order_value
        }

    state_file = os.path.join(output_dir, "states.json")

    if os.path.exists(state_file):
        with open(state_file, "r") as file:
            data = json.load(file)
    else:
        data = []

    data.append(state)

    with open(state_file, "w") as file:
        json.dump(data, file, indent=4)


def execute_order(robot: GripperRobot, order: Tuple[OrderType, List[float]], output_dir: str, start_time: float, reverse_xy: bool = False):
    """
    Execute a single order on the robot and save its state.

    :param robot: The robot to execute the order
    :param order: A tuple containing the OrderType and the values associated with the order
    :param output_dir: Directory to save state data
    :param start_time: The start time of the autograsper process
    :param reverse_xy: If True, reverse the x and y coordinates (new_x = 1 - x, new_y = 1 - y)

    BA reverse_xy is a temporary fix caused by the transfer from old to new API
    old API matrix transformations regarding position gathering from images is not updated
    a proper fix should be implemented
    """
    try:
        order_type, order_value = order
        if order_type == OrderType.MOVE_XY:
            if reverse_xy:
                order_value[0] = 1 - order_value[0]
                # order_value[1] = 1 - order_value[1]
            robot.move_xy(order_value[0], order_value[1])
            print("Moved XY to", order_value)
        elif order_type == OrderType.MOVE_Z:
            robot.move_z(order_value[0])
            print("Moved Z to", order_value[0])
        elif order_type == OrderType.GRIPPER_OPEN:
            robot.gripper_open(5)
            print("Gripper opened")
        elif order_type == OrderType.GRIPPER_CLOSE:
            robot.gripper_close()
            print("Gripper closed")

        save_state(robot, output_dir, start_time, order)

    except (IndexError, ValueError) as e:
        print(f"Error executing order {order}: {e}")


def queue_orders(
    robot: GripperRobot,
    order_list: List[Tuple[OrderType, List[float]]],
    time_between_orders: float,
    output_dir: str = "",
    start_time: float = -1.0,
    reverse_xy: bool = False
):
    """
    Queue a list of orders for the robot to execute sequentially and save state after each order.

    :param robot: The robot to execute the orders
    :param order_list: A list of tuples containing OrderType and the associated values
    :param time_between_orders: Time to wait between executing orders
    :param output_dir: Directory to save state data
    :param start_time: The start time of the autograsper process
    """
    for order in order_list:
        execute_order(robot, order, output_dir, start_time, reverse_xy)
        time.sleep(time_between_orders)


def queue_orders_with_input(
    robot: GripperRobot, order_list: List[Tuple[OrderType, List[float]]], output_dir: str = "", start_time: float = -1.0
):
    """
    Queue a list of orders for the robot to execute sequentially, waiting for user input between each command, and save state after each order.

    :param robot: The robot to execute the orders
    :param order_list: A list of tuples containing OrderType and the associated values
    :param output_dir: Directory to save state data
    :param start_time: The start time of the autograsper process
    """
    for order in order_list:
        try:
            order_type, order_value = order
            if order_type == OrderType.MOVE_XY:
                print(f"Intended command: Move XY to {order_value}")
                input("Press Enter to execute...")
            elif order_type == OrderType.MOVE_Z:
                print(f"Intended command: Move Z to {order_value[0]}")
                input("Press Enter to execute...")
            elif order_type == OrderType.GRIPPER_OPEN:
                print("Intended command: Gripper Open")
                input("Press Enter to execute...")
            elif order_type == OrderType.GRIPPER_CLOSE:
                print("Intended command: Gripper Close")
                input("Press Enter to execute...")

            execute_order(robot, order, output_dir, start_time)
        except (IndexError, ValueError) as e:
            print(f"Error executing order {order}: {e}")


def snowflake_sweep(robot: GripperRobot):
    """
    Perform a snowflake sweep pattern with the robot.

    :param robot: The robot to perform the sweep
    :param output_dir: Directory to save state data
    :param start_time: The start time of the autograsper process
    """
    time_between_orders = 2
    order_list = []
    for z in range(5, 0, -1):
        height = z * 0.2
        order_list.append((OrderType.MOVE_Z, [height]))

        coordinates = (
            [(x * 0.1, 0.0) for x in range(0, 10)]
            + [(1.0, y * 0.1) for y in range(0, 10)]
            + [(x * 0.1, 1.0) for x in range(10, 0, -1)]
            + [(0.0, y * 0.1) for y in range(10, 0, -1)]
        )

        for coord in coordinates:
            order_list.append((OrderType.MOVE_XY, list(map(float, coord))))
            order_list.append((OrderType.MOVE_XY, [0.5, 0.5]))

    queue_orders(robot, order_list, time_between_orders)
    print("Snowflake sweep complete")


def sweep_straight(robot: GripperRobot):
    """
    Perform a straight sweep pattern with the robot.

    :param robot: The robot to perform the sweep
    :param output_dir: Directory to save state data
    :param start_time: The start time of the autograsper process
    """
    time_between_orders = 2
    order_list = []
    y_pos = 0

    for z in range(5, 2, -1):
        order_list.append((OrderType.MOVE_Z, [z * 0.2]))

        for x in range(0, 10):
            y_pos = 1 - y_pos
            order_list.append((OrderType.MOVE_XY, [x * 0.1, y_pos]))

    queue_orders(robot, order_list, time_between_orders)
    print("Straight sweep complete")


def recover_gripper(robot: GripperRobot):
    """
    Recover the gripper by fully opening and then closing it.

    :param robot: The robot to perform the recovery
    """
    try:
        robot.gripper_fully_open()
        time.sleep(1)
        robot.gripper_close()
        time.sleep(1)
    except Exception as e:
        print(f"Error recovering gripper: {e}")


def generate_position_grid() -> np.ndarray:
    """
    Generate a grid of positions.

    :return: A numpy array of grid positions
    """
    x = np.arange(0.1, 1, 0.05)
    y = np.arange(0.1, 1, 0.05)
    position_bank = np.array(np.meshgrid(x, y)).T.reshape(-1, 2)
    return position_bank


def pick_random_positions(
    position_bank: np.ndarray,
    n_layers: int,
    object_size: float,
    avoid_positions: Optional[List[np.ndarray]] = None,
) -> List[np.ndarray]:
    """
    Pick random positions from the position bank ensuring they are spaced apart by object_size.

    :param position_bank: A numpy array of available positions
    :param n_layers: Number of positions to pick
    :param object_size: Minimum distance between positions
    :param avoid_positions: A list of positions to avoid when picking new positions
    :return: A list of selected positions
    """
    if avoid_positions is None:
        avoid_positions = [np.array([0.5, 0.5])]

    positions: List[np.ndarray] = []
    while len(positions) < n_layers:
        position_index = np.random.randint(0, len(position_bank))
        position = position_bank[position_index]
        if all(
            np.linalg.norm(position - p) > object_size
            for p in positions + avoid_positions
        ):
            positions.append(position)
    return positions


def get_undistorted_bottom_image(
    robot: GripperRobot, m: np.ndarray, d: np.ndarray
) -> np.ndarray:
    """
    Get an undistorted image from the robot's camera.

    :param robot: The robot to capture the image
    :param m: Camera matrix for undistortion
    :param d: Distortion coefficients
    :return: An undistorted image
    """
    image, _ = robot.getImageBase()
    return undistort(image, m, d)
