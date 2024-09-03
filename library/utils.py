import json
import os
import time
from enum import Enum
from typing import Any, List, Optional, Tuple

import numpy as np
from pynput import keyboard

from client.cloudgripper_client import GripperRobot
from library.calibration import undistort


class OrderType(Enum):
    MOVE_XY = 1
    MOVE_Z = 2
    GRIPPER_CLOSE = 3
    GRIPPER_OPEN = 4


def write_order(
    output_dir: str,
    order_time: float,
    previous_order: Optional[Tuple[Any, List[float]]] = None,
):
    """
    Save the previous order to the orders.json file.

    :param output_dir: Directory to save order data
    :param start_time: The start time of the autograsper process
    :param previous_order: The previous order executed by the robot
    """
    if previous_order is None:
        return

    order_type, order_value = previous_order

    # Convert order_value to list if it's not already
    order_value = [float(v) for v in order_value]

    order = {
        "order_type": order_type.name,
        "order_value": order_value,
        "time": order_time,
    }

    orders_file = os.path.join(output_dir, "orders.json")

    if os.path.exists(orders_file):
        with open(orders_file, "r") as file:
            data = json.load(file)
    else:
        data = []

    data.append(order)

    with open(orders_file, "w") as file:
        json.dump(data, file, indent=4)


def execute_order(
    robot: GripperRobot,
    order: Tuple[OrderType, List[float]],
    output_dir: str,
    reverse_xy: bool = False,
):
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

        order_value = np.clip(order_value, 0, 1)

        start_time = 0

        if order_type == OrderType.MOVE_XY and reverse_xy:
            order_value[0] = 1 - order_value[0]

        if order_type == OrderType.MOVE_XY:
            start_time = robot.move_xy(order_value[0], order_value[1])
            robot.order_count += 1
        elif order_type == OrderType.MOVE_Z:
            start_time = robot.move_z(order_value[0])
            robot.order_count += 1
        elif order_type == OrderType.GRIPPER_OPEN:
            start_time = robot.gripper_open()
            robot.order_count += 1
        elif order_type == OrderType.GRIPPER_CLOSE:
            if len(order_value) != 0:
                start_time = robot.move_gripper(order_value[0])
                robot.order_count += 1
            else:
                current_position = 0.3
                end_position = 0.20
                step = 0.02
                wait_time = 0.05
                start_time = robot.move_gripper(current_position)
                while current_position >= end_position:
                    robot.order_count += 1
                    robot.move_gripper(current_position)
                    time.sleep(wait_time)
                    current_position -= step

        if output_dir != "":
            write_order(output_dir, start_time, order)

            time.sleep(1)  # buffer time

    except (IndexError, ValueError) as e:
        print(f"Error executing order {order}: {e}")


def queue_orders(
    robot: GripperRobot,
    order_list: List[Tuple[OrderType, List[float]]],
    time_between_orders: float,
    output_dir: str = "",
    reverse_xy: bool = False,
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
        execute_order(robot, order, output_dir, reverse_xy)
        time.sleep(time_between_orders)


def queue_orders_with_input(
    robot: GripperRobot,
    order_list: List[Tuple[OrderType, List[float]]],
    output_dir: str = "",
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

            execute_order(robot, order, output_dir)
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

    for z in range(2, 0, -1):
        height = z * 0.2

        order_list.append((OrderType.GRIPPER_CLOSE, []))
        order_list.append((OrderType.MOVE_Z, [height]))

        coordinates = (
            [(x * 0.1, 0.0) for x in range(3, 6)]
            + [(1.0, y * 0.1) for y in range(3, 6)]
            + [(x * 0.1, 1.0) for x in range(6, 3, -1)]
            + [(0.0, y * 0.1) for y in range(6, 3, -1)]
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
    x = np.arange(0.15, 0.85, 0.05)
    y = np.arange(0.15, 0.85, 0.05)
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
    image, _ = robot.get_image_base()
    return undistort(image, m, d)


def run_calibration(height, robot):
    commands = [
        (OrderType.GRIPPER_CLOSE, []),
        (OrderType.MOVE_Z, [1.0]),
        (OrderType.MOVE_XY, [0.0, 0.0]),
        (OrderType.MOVE_Z, [height]),
        (OrderType.MOVE_Z, [1.0]),
        (OrderType.MOVE_XY, [1.0, 0.0]),
        (OrderType.MOVE_Z, [height]),
        (OrderType.MOVE_Z, [1.0]),
        (OrderType.MOVE_XY, [0.0, 1.0]),
        (OrderType.MOVE_Z, [height]),
        (OrderType.MOVE_Z, [1.0]),
        (OrderType.MOVE_XY, [1.0, 1.0]),
        (OrderType.MOVE_Z, [height]),
    ]

    queue_orders_with_input(robot, commands)


def convert_ndarray_to_list(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: convert_ndarray_to_list(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarray_to_list(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj


def manual_control(robot):
    """
    Manually control the robot using keyboard inputs.
    """
    current_x = 0.0
    current_y = 0.0
    current_z = 0.0
    current_rotation = 0
    current_angle = 0.4

    def on_press(key):
        nonlocal current_x, current_y, current_z, current_rotation, current_angle
        try:
            if key.char == "w":
                current_y += 0.1
                current_y = min(max(current_y, 0), 1)
                robot.move_xy(current_x, current_y)
            elif key.char == "a":
                current_x -= 0.1
                current_x = min(max(current_x, 0), 1)
                robot.move_xy(current_x, current_y)
            elif key.char == "s":
                current_y -= 0.1
                current_y = min(max(current_y, 0), 1)
                robot.move_xy(current_x, current_y)
            elif key.char == "x":
                current_y -= 0.05
                current_y = min(max(current_y, 0), 1)
                robot.move_xy(current_x, current_y)
            elif key.char == "z":
                current_y -= 0.01
                current_y = min(max(current_y, 0), 1)
                robot.move_xy(current_x, current_y)
            elif key.char == "d":
                current_x += 0.1
                current_x = min(max(current_x, 0), 1)
                robot.move_xy(current_x, current_y)
            elif key.char == "r":
                current_z += 0.1
                current_z = min(max(current_z, 0), 1)
                print(current_z)
                robot.move_z(current_z)
            elif key.char == "f":
                current_z -= 0.1
                current_z = min(max(current_z, 0), 1)
                print(current_z)
                robot.move_z(current_z)
            elif key.char == "i":
                current_angle += 0.05
                current_angle = min(current_angle, 1)
                print(current_angle)
                robot.move_gripper(current_angle)
            elif key.char == "o":
                current_angle += 0.01
                current_angle = min(current_angle, 1)
                print(current_angle)
                robot.move_gripper(current_angle)
            elif key.char == "p":
                current_angle -= 0.01
                current_angle = max(current_angle, 0.2)
                print(current_angle)
                robot.move_gripper(current_angle)
            elif key.char == "q":
                current_rotation -= 10
                robot.rotate(current_rotation)
            elif key.char == "e":
                current_rotation += 10
                robot.rotate(current_rotation)
            elif key.char == "n":
                robot.gripper_open()
                time.sleep(1)
                robot.move_z(0)
                time.sleep(1)
                robot.move_gripper(0.5)
                time.sleep(1)
                robot.move_z(1)
                time.sleep(1)
                robot.move_xy(min(current_x + 0.2, 1), min(current_y + 0.2, 1))
                time.sleep(1)
                robot.move_xy(current_x, current_y)
                time.sleep(1)
                robot.move_z(0)
                time.sleep(1)
        except Exception as e:
            print(e)

    def on_release(key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def clear_center(robot):
    """
    Clear the center area of the workspace.
    """
    print("clearing center")
    commands = [
        (OrderType.MOVE_Z, [1]),
        (OrderType.GRIPPER_CLOSE, []),
        (OrderType.MOVE_XY, [0.3, 0.3]),
        (OrderType.MOVE_Z, [0.4]),
        (OrderType.MOVE_XY, [0.5, 0.3]),
        (OrderType.MOVE_XY, [0.5, 0.7]),
        (OrderType.MOVE_XY, [0.3, 0.7]),
        (OrderType.MOVE_Z, [0.1]),
        (OrderType.MOVE_XY, [0.3, 0.5]),
        (OrderType.MOVE_XY, [0.7, 0.5]),
        (OrderType.MOVE_XY, [0.3, 0.3]),
        (OrderType.MOVE_XY, [0.5, 0.5]),
        (OrderType.MOVE_XY, [0.7, 0.7]),
        (OrderType.MOVE_XY, [0.7, 0.5]),
        (OrderType.MOVE_XY, [0.7, 0.3]),
        (OrderType.MOVE_XY, [0.5, 0.5]),
        (OrderType.MOVE_XY, [0.3, 0.7]),
        (OrderType.MOVE_Z, [1]),
    ]

    queue_orders(robot, commands, 1)
    print("clearing center complete")
