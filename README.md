# CloudGripper API Client

Welcome to the CloudGripper API! This project provides a Python interface to remotely interact with the CloudGripper robot.

## Table of Contents

1. [Introduction](#introduction)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Methods](#methods)
6. [Color Picker](#color-picker)
7. [Utilities](#utilities)
8. [Example Projects](#example-projects)
   - [Autograsper](#example-project-autograsper)
   - [Recorder](#example-project-recorder)
   - [Large Scale Data Collection](#example-project-large-scale-data-collection)

## Introduction

The CloudGripper API Client is designed to facilitate communication with the CloudGripper robot. The client includes functions to control the robot's movements, operate its gripper, retrieve images from its cameras, perform color calibration, and manage orders for the robot.

## Installation

To install the CloudGripper API Client, follow these steps:

```bash
# Clone the repository
git clone https://github.com/yourusername/cloudgripper-client.git
cd cloudgripper-client

# Install the required dependencies
pip install -r requirements.txt
```

## Usage

Here's an example of how to use the CloudGripper API Client to control a robot:

```python
from client.cloudgripper_client import GripperRobot

# Initialize the robot client
robot = GripperRobot(name='robot1', token='your_api_token_here')

# Get the robot's current state
state, timestamp = robot.get_state()
print(f"State: {state}, Timestamp: {timestamp}")

# Move the robot
robot.step_forward()
robot.step_backward()
robot.step_left()
robot.step_right()

# Operate the gripper
robot.gripper_open()
robot.gripper_close()

# Retrieve images
base_image, base_timestamp, _ = robot.get_image_base()
top_image, top_timestamp = robot.get_image_top()
```

## Methods

### Initialization

```python
robot = GripperRobot(name='robot1', token='your_api_token_here')
```

### Basic Movements

- `step_forward()`: Move the robot one step forward.
- `step_backward()`: Move the robot one step backward.
- `step_left()`: Move the robot one step to the left.
- `step_right()`: Move the robot one step to the right.

### Gripper Operations

- `gripper_open()`: Open the robot's gripper.
- `gripper_close()`: Close the robot's gripper.
- `move_gripper(angle)`: Move the gripper to a specific angle.

### Rotations and Movements

- `rotate(angle)`: Rotate the robot to a specified angle.
- `move_z(z)`: Move the robot along the Z-axis.
- `move_xy(x, y)`: Move the robot along the X and Y axes.

### Image Retrieval

- `get_image_base()`: Get the base image from the robot's camera.
- `get_image_top()`: Get the top image from the robot's camera.
- `get_all_states()`: Get the combined state and images from the robot.

### State Retrieval

- `get_state()`: Get the current state of the robot.
- `calibrate()`: Calibrate the robot.

## Color-Picker

The `rgb_color_picker.py` script provides functionality for color calibration and object tracking within images.

### Usage

You can use the script from the command line as follows:

```bash
python library/rgb_color_picker.py <image_file> <colors>
```

Example:

```bash
python library/rgb_color_picker.py sample_image.jpg red green orange
```

### Functions

#### `test_calibration(image, colors)`

Tests the calibration of specified colors in the given image.

#### `all_objects_are_visible(objects, image, DEBUG=False)`

Checks if all specified objects are visible in the image.

#### `object_tracking(image, color="red", size_threshold=290, DEBUG=False, debug_image_path="debug_image.png")`

Tracks objects of a specified color in the image and returns their positions.

### Example

```python
import cv2
from library.rgb_color_picker import object_tracking

# Load the image
image = cv2.imread("sample_image.jpg")

# Track red objects
position = object_tracking(image, color="red", DEBUG=True, debug_image_path="debug_red.png")
print("Position of red object:", position)
```

## Utilities

The `utils.py` script provides a set of utility functions for managing robot orders, executing complex sequences, and handling image data.

### Functions

#### `write_order(output_dir: str, start_time: float, previous_order: Optional[Tuple[Any, List[float]]] = None)`

Save the previous order to the `orders.json` file.

#### `execute_order(robot: GripperRobot, order: Tuple[OrderType, List[float]], output_dir: str, reverse_xy: bool = False)`

Execute a single order on the robot and save its state.

#### `queue_orders(robot: GripperRobot, order_list: List[Tuple[OrderType, List[float]]], time_between_orders: float, output_dir: str = "", reverse_xy: bool = False)`

Queue a list of orders for the robot to execute sequentially and save state after each order.

#### `queue_orders_with_input(robot: GripperRobot, order_list: List[Tuple[OrderType, List[float]]], output_dir: str = "", start_time: float = -1.0)`

Queue a list of orders for the robot to execute sequentially, waiting for user input between each command, and save state after each order.

#### `snowflake_sweep(robot: GripperRobot)`

Perform a snowflake sweep pattern with the robot.

#### `sweep_straight(robot: GripperRobot)`

Perform a straight sweep pattern with the robot.

#### `recover_gripper(robot: GripperRobot)`

Recover the gripper by fully opening and then closing it.

#### `generate_position_grid() -> np.ndarray`

Generate a grid of positions.

#### `pick_random_positions(position_bank: np.ndarray, n_layers: int, object_size: float, avoid_positions: Optional[List[np.ndarray]] = None) -> List[np.ndarray]`

Pick random positions from the position bank ensuring they are spaced apart by object_size.

#### `get_undistorted_bottom_image(robot: GripperRobot, m: np.ndarray, d: np.ndarray) -> np.ndarray`

Get an undistorted image from the robot's camera.

#### `convert_ndarray_to_list(obj: Any) -> Any`

Convert a numpy ndarray to a Python list.

### Example

```python
from client.cloudgripper_client import GripperRobot
from library.utils import generate_position_grid, pick_random_positions

# Initialize the robot client
robot = GripperRobot(name='robot1', token='your_api_token_here')

# Generate a grid of positions
position_grid = generate_position_grid()

# Pick random positions ensuring minimum distance
positions = pick_random_positions(position_grid, n_layers=5, object_size=0.1)
print("Selected positions:", positions)
```

## Example-projects

### Example Project: Autograsper

The `autograsper.py` script demonstrates how to use the CloudGripper API Client to perform a stacking task. This example includes initialization, calibration, object tracking, and task execution.

#### Usage

To run the Autograsper script, use the following command:

```bash
python stack_from_scratch/autograsper.py --robot_idx <robot_idx> --output_dir <output_dir>
```

Example:

```bash
python stack_from_scratch/autograsper.py --robot_idx robot1 --output_dir ./output
```

#### Main Components

##### Autograsper

The main class responsible for managing the robot's tasks and state.

- `__init__(self, args, output_dir="")`: Initialize the Autograsper with the provided arguments.
- `pickup_and_place_object(self, object_position, object_height, target_height, target_position=[0.5, 0.5], time_between_orders=3)`: Pickup and place an object from one position to another.
- `reset(self, block_positions, block_heights, stack_position=[0.5, 0.5], time_between_orders=2)`: Reset the blocks to their initial positions.
- `clear_center(self)`: Clear the center area of the workspace.
- `startup(self, position)`: Perform startup sequence at a given position.


- `run_calibration(self, height)`: Run the calibration process.
- `recover_after_fail(self)`: Recover the robot after a failure.
- `get_block_pos(self, color, debug=False)`: Get the position of a block of a specified color.
- `run_grasping(self)`: Run the main grasping loop.
- `go_to_corner(self)`: Move the robot to a corner position.
- `manual_control(self)`: Manually control the robot using keyboard inputs.

#### Example

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autograsper Robot Controller")
    parser.add_argument("--robot_idx", type=str, required=True, help="Robot index")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    autograsper = Autograsper(args, args.output_dir)
    autograsper.run_grasping()
```

### Example Project: Recorder

The `recorder.py` script demonstrates how to record and save robot data, including capturing video from the robot's cameras and saving its state to a file.

#### Usage

To run the Recorder script, use the following command:

```bash
python stack_from_scratch/recorder.py --session_id <session_id> --output_dir <output_dir> --robot_idx <robot_idx>
```

Example:

```bash
python stack_from_scratch/recorder.py --session_id session1 --output_dir ./output --robot_idx robot1
```

#### Main Components

##### Recorder

The main class responsible for recording video and saving the robot's state.

- `__init__(self, session_id: str, output_dir: str, m: Any, d: Any, token: str, idx: str)`: Initialize the Recorder with the provided parameters.
- `record(self, start_new_video_every: int = 30)`: Record video with optional periodic video restarts.
- `write_final_image(self)`: Write the final image from the top camera.
- `start_new_recording(self, new_output_dir: str)`: Start a new recording session with a new output directory.
- `stop(self)`: Set the stop flag to terminate recording.
- `save_state(self, robot: Any)`: Save the state of the robot to a JSON file.

#### Example

```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Recorder for CloudGripper Robot")
    parser.add_argument("--session_id", type=str, required=True, help="Session ID")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory")
    parser.add_argument("--robot_idx", type=str, required=True, help="Robot index")
    args = parser.parse_args()

    m = np.array(
        [
            [505.24537524391866, 0.0, 324.5096286632362],
            [0.0, 505.6456651337437, 233.54118730278543],
            [0.0, 0.0, 1.0],
        ]
    )
    d = np.array(
        [
            -0.07727407195057368,
            -0.047989733519315944,
            0.12157420705123315,
            -0.09667542135039282,
        ]
    )

    token = os.getenv("ROBOT_TOKEN", "default_token")

    recorder = Recorder(args.session_id, args.output_dir, m, d, token, args.robot_idx)
    recorder.record()
```

### Example Project: Large Scale Data Collection

The `collect_data_stacking.py` script demonstrates how to use the Autograsper and Recorder together to perform a large-scale data collection task. This example includes setting up the Autograsper and Recorder, monitoring the robot's state, and handling errors.

#### Usage

To run the data collection script, use the following command:

```bash
python stack_from_scratch/collect_data_stacking.py --robot_idx <robot_idx>
```

Example:

```bash
python stack_from_scratch/collect_data_stacking.py --robot_idx robot1
```

#### Main Components

- `get_new_session_id(base_dir)`: Generate a new session ID.
- `run_autograsper(autograsper)`: Run the Autograsper.
- `setup_recorder(output_dir, robot_idx)`: Set up the Recorder.
- `run_recorder(recorder)`: Run the Recorder.
- `state_monitor(autograsper)`: Monitor the state of the Autograsper.
- `check_stacking_success()`: Check if the stacking task was successful.
- `handle_error(e)`: Handle errors and set the error event.
- `bottom_image_monitor(recorder, autograsper)`: Monitor the bottom image and update the Autograsper.

#### Example

For the complete example, please refer to the `collect_data_stacking.py` script in the repository.



---

For more detailed documentation and examples, please refer to the source code and docstrings provided in each method. If you encounter any issues or have questions, feel free to open an issue on GitHub.
