# Project Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Directory Structure](#directory-structure)
3. [Modules Overview](#modules-overview)
    - [library/utils.py](#libraryutilspy)
    - [stack_from_scratch/autograsper.py](#stack_from_scratchautograsperpy)
    - [stack_from_scratch/recording.py](#stack_from_scratchrecordingpy)
    - [stack_from_scratch/collect_data_stacking.py](#stack_from_scratchcollect_data_stackingpy)
4. [Usage](#usage)
5. [Dependencies](#dependencies)

## Introduction
This project involves the automation of robotic gripping tasks using a GripperRobot. The main functionalities include executing specific orders, recording the robot's actions, and collecting data for stacking tasks.

## Directory Structure
- `library/`
  - `utils.py`
- `stack_from_scratch/`
  - `autograsper.py`
  - `recording.py`
  - `collect_data_stacking.py`

## Modules Overview

### library/utils.py

#### Imports
- **Standard Libraries**: `time`, `json`, `os`
- **External Libraries**: `numpy`
- **Project Modules**: `GripperRobot` from `client.cloudgripper_client`, `undistort` from `library.calibration`

#### Enums
- `OrderType`: Enum to define different types of robot orders (MOVE_XY, MOVE_Z, GRIPPER_CLOSE, GRIPPER_OPEN).

#### Functions
- `save_state(robot, output_dir, start_time, previous_order)`: Saves the current state of the robot.
- `execute_order(robot, order, output_dir, start_time, reverse_xy)`: Executes a single order on the robot.
- `queue_orders(robot, order_list, time_between_orders, output_dir, start_time, reverse_xy)`: Queues and executes a list of orders sequentially.
- `queue_orders_with_input(robot, order_list, output_dir, start_time)`: Queues and executes orders with user input between commands.
- `snowflake_sweep(robot)`: Performs a snowflake sweep pattern with the robot.
- `sweep_straight(robot)`: Performs a straight sweep pattern with the robot.
- `recover_gripper(robot)`: Recovers the gripper by fully opening and then closing it.
- `generate_position_grid()`: Generates a grid of positions.
- `pick_random_positions(position_bank, n_layers, object_size, avoid_positions)`: Picks random positions from a grid.
- `get_undistorted_bottom_image(robot, m, d)`: Gets an undistorted image from the robot's camera.

### stack_from_scratch/autograsper.py

#### Imports
- **Standard Libraries**: `dotenv`, `numpy`, `time`, `random`, `argparse`, `os`, `sys`
- **Project Modules**: Various utilities and classes from `library.utils`, `library.rgb_object_tracker`, `library.Camera2Robot`, `library.calibration`, and `client.cloudgripper_client`.

#### Classes
- `RobotActivity`: Enum to define different states of the robot (ACTIVE, RESETTING, FINISHED, STARTUP).
- `Autograsper`: Main class to handle the autograsping process.

#### Methods
- `__init__(self, args, output_dir)`: Initializes the Autograsper.
- `pickup_and_place_object(self, object_position, object_height, target_height, target_position, time_between_orders)`: Picks up and places an object.
- `reset(self, block_positions, block_heights, stack_position, time_between_orders)`: Resets the blocks to their initial positions.
- `clear_center(self)`: Clears the center area of the workspace.
- `startup(self, position)`: Performs a startup sequence at a given position.
- `run_grasping(self)`: Runs the main grasping loop.

#### Main Execution
- Sets up command-line argument parsing and initializes the `Autograsper` instance to start the grasping process.

### stack_from_scratch/recording.py

#### Imports
- **Standard Libraries**: `argparse`, `os`, `time`, `cv2`, `sys`
- **Project Modules**: Various utilities from `client.cloudgripper_client`, `library.bottom_image_preprocessing`, `library.calibration`, `library.Camera2Robot`, `library.object_tracking`, and `library.utils`.

#### Classes
- `Recorder`: Main class to handle the recording of the robot's actions.

#### Methods
- `__init__(self, session_id, output_dir, m, d, token, idx)`: Initializes the Recorder.
- `_start_new_video(self, output_video_dir, output_bottom_video_dir, video_counter, fourcc, image_shape, bottom_image_shape)`: Starts a new video recording session.
- `record(self, start_new_video_every)`: Records the robot's actions.
- `_initialize_directories(self)`: Initializes the directories for saving recordings.
- `start_new_recording(self, new_output_dir)`: Starts a new recording in a different directory.
- `stop(self)`: Stops the recording process.

#### Main Execution
- Sets up command-line argument parsing and initializes the `Recorder` instance to start recording.

### stack_from_scratch/collect_data_stacking.py

#### Imports
- **Standard Libraries**: `os`, `argparse`, `time`, `threading`, `numpy`
- **Project Modules**: `Recorder` from `recording`, `Autograsper`, `RobotActivity` from `autograsper`.

#### Functions
- `get_new_session_id(base_dir)`: Generates a new session ID based on existing directories.
- `run_autograsper(autograsper)`: Runs the autograsper process.
- `setup_recorder(output_dir, robot_idx)`: Sets up the recorder with given parameters.
- `run_recorder(recorder)`: Runs the recorder process.
- `state_monitor(autograsper)`: Monitors the state of the autograsper.

#### Main Execution
- Sets up command-line argument parsing and initializes the `Autograsper` and `Recorder` instances to run in parallel. It monitors their states and manages session directories.

# Usage Guide

## Setting Up Your Environment

Before using the code, ensure you have set up your environment correctly. This includes installing necessary dependencies and setting up environment variables.

### Step 1: Install Dependencies

Ensure you have Python 3.x installed. Install the required Python packages using pip:

```sh
pip install numpy opencv-python python-dotenv
```

### Step 2: Set Environment Variables

The code requires an environment variable `ROBOT_TOKEN` to authenticate with the GripperRobot API. Create a `.env` file in the project root with the following content:

```env
ROBOT_TOKEN=your_robot_token_here
```

## Running the Code

### Running the Autograsper

The `autograsper.py` script is the core component that controls the robot to perform grasping tasks.

1. **Command-Line Arguments**:
   - `--robot_idx`: The index of the robot to be controlled.
   - `--output_dir`: The directory to save state data.

2. **Example Command**:
   ```sh
   python stack_from_scratch/autograsper.py --robot_idx 1 --output_dir /path/to/output
   ```

3. **Description**:
   - Initializes the `Autograsper` class.
   - Runs the main grasping loop, where the robot performs a series of tasks such as moving, gripping, and placing objects.
   - Saves the state of the robot after each action for later analysis.

### Recording the Robot's Actions

The `recording.py` script records the robot's actions, capturing both top and bottom camera views.

1. **Command-Line Arguments**:
   - `--robot_idx`: The index of the robot to be recorded.
   - `--output_dir`: The directory to save recorded videos and final images.

2. **Example Command**:
   ```sh
   python stack_from_scratch/recording.py --robot_idx 1 --output_dir /path/to/output
   ```

3. **Description**:
   - Initializes the `Recorder` class.
   - Records the robot's actions, saving video files at specified intervals.
   - Displays the bottom camera view and waits for user input to stop recording.

### Example: Collecting Data for Stacking

The `collect_data_stacking.py` script combines the functionality of `autograsper.py` and `recording.py` to automate data collection for stacking tasks.

1. **Command-Line Arguments**:
   - `--robot_idx`: The index of the robot to be controlled and recorded.

2. **Example Command**:
   ```sh
   python stack_from_scratch/collect_data_stacking.py --robot_idx 1
   ```

3. **Description**:
   - Initializes the `Autograsper` and `Recorder` classes.
   - Runs the autograsper and recorder in parallel threads.
   - Monitors the state of the autograsper and manages recording sessions based on the robot's activity state.
   - Creates new data points and organizes the output into structured directories.

#### Detailed Workflow

1. **Initialization**:
   - The `Autograsper` initializes with command-line arguments, setting up the robot and its parameters.
   - The `Recorder` initializes with a session ID, output directory, camera calibration parameters, and robot token.

2. **Running the Autograsper**:
   - The autograsper performs a series of actions such as moving to specific coordinates, opening and closing the gripper, and stacking objects.
   - Each action's state is saved for later analysis.

3. **Recording Sessions**:
   - The recorder captures video frames from the robot's cameras.
   - Videos are saved in the specified output directory.
   - The bottom camera view is displayed for real-time monitoring.

4. **State Monitoring**:
   - The `collect_data_stacking.py` script monitors the autograsper's state.
   - When the robot's state changes, the script handles the transition, creating new data points and managing recording sessions accordingly.
   - The script ensures that recording continues seamlessly through state changes, such as resetting or completing tasks.

### Example: Generic Workflow

To illustrate a typical workflow:

1. **Start a Grasping Session**:
   ```sh
   python stack_from_scratch/autograsper.py --robot_idx 1 --output_dir /path/to/output
   ```

2. **Record the Session**:
   ```sh
   python stack_from_scratch/recording.py --robot_idx 1 --output_dir /path/to/output
   ```

3. **Automate Data Collection**:
   ```sh
   python stack_from_scratch/collect_data_stacking.py --robot_idx 1
   ```
