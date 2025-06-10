# CloudGripper Client Library

The CloudGripper API Client library provides a Python client to communicate with and control robotic arms over a cloud-based API. 

## Features

- Supports multiple robot instances.
- Simple functions to send commands and fetch robot state.
- Allows image fetching from robot cameras.

## Setup

Set up a Python virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Getting Started

1. **Setting up the Client**:

   First, ensure that your token for the CloudGripper API is set as an environment variable named `CLOUDGRIPPER_TOKEN`. Ensure you keep this token secure and do not share it publicly.
   ```
   export CLOUDGRIPPER_TOKEN="YOUR_TOKEN"
   ```

2. **Importing and Initializing the GripperRobot class**:

   Import the required libraries and classes.

   ```python
   import os
   from client.cloudgripper_client import GripperRobot
   ```

   Initialize the robot object by specifying its name and your API token. Name is typically in the format `robotX`, where `X` is the specific number of the robot assigned to you.

   ```python
   token = os.environ['CLOUDGRIPPER_TOKEN']
   robot = GripperRobot('robotX', token)
   ```

3. **Sending Commands**:

   Use the robot object to send commands and control the robot.

   ```python
   robot.gripper_open()   # Opens the gripper
   robot.step_forward()   # Moves the robot forward
   ```

4. **Fetching Robot State and Images**:

   Retrieve the robot's state:

   ```python
   state, timestamp = robot.get_state()
   print(f'state = {state}, time_stamp = {timestamp}')
   ```

   Fetch images from robot cameras:

   ```python
   frame, timestamp = robot.getImage()   # Get bottom camera image
   ```

5. **Streaming Camera Feed**:

   You can also fetch continuous camera feed from the robot and display it using OpenCV.

   ```python
   import cv2

   while True:
       image, timestamp = robot.getImageTop()
       cv2.imshow("Cloudgripper top camera stream", image)
       if cv2.waitKey(1) & 0xFF == ord('q'):
           break
   ```

   Ensure you have OpenCV (`opencv-python`) installed to use this feature.

## Commands Overview

Here are some of the basic commands you can send using the CloudGripper library:

- Movement:
  - `robot.step_forward()`
  - `robot.step_backward()`
  - `robot.step_left()`
  - `robot.step_right()`
  
- Rotation and Movement:
  - `robot.rotate(angle)`   # Rotation in degrees (0 to 180)
  - `robot.move_z(z)`       # Move up or down, z value normalized between 0 and 1
  - `robot.move_xy(x, y)`   # Move to the specific x and y position, x,y normalized between 0 and 1 to cover work area

- Gripper Control:
  - `robot.gripper_open()`   # Opens the gripper fully
  - `robot.gripper_close()`  # Closes the gripper fully
  - `robot.move_gripper(val)` # Adjusts the gripper's opening to a specific value, where 0 is fully close and 1 is fully open

- Fetch State and Image:
  - `robot.get_state()`
  - `robot.getImageBase()`
  - `robot.getImageTop()`

## Important Note

- Ensure you have a stable internet connection as the client communicates with the robots over the internet.

---

# CloudGripper Mock API

This repository also contains a mock implementation of the CloudGripper robot class for development and testing purposes.

## Overview

The `GripperRobotMock` class simulates the behavior of a CloudGripper robot class, allowing developers to test their code without requiring access to a physical robot. The mock implementation includes:

- Robot movement commands (x, y, z axes)
- Gripper control (open/close)
- Rotation control
- Empty Camera image
- Realistic error handling with configurable failure rates

For testing purposes, the mock implementation will use a default token if none is provided.

## Usage Examples

### Basic Usage

```python
from client.cloudgripper_client_mock import GripperRobotMock

# Initialize a mock robot with ID and authentication token
# This mocks a real robot connection without requiring hardware
robot = GripperRobotMock('robot6', 'your-token-here')

# Get the mock robot state (position, gripper status, etc.)
# Returns a dictionary with robot parameters and a timestamp
state, timestamp = robot.get_state()
print(f"Robot state: {state}")

# Mock precise XY movement (values normalized between 0-1)
# 0.5, 0.7 represents moving to center-right of the work area
robot.move_xy(0.5, 0.7)

# Mock vertical movement (0=bottom, 1=top)
# 0.8 positions the robot arm near the top of its vertical range
robot.move_z(0.8)

# Mock gripper operations with realistic timing
robot.gripper_open() # Fully opens the mock gripper, mimicking a real gripper's timing
robot.gripper_close() # Fully closes the mock gripper, with emulated closing force

# Mock camera images (returns blank frames with timestamps)
img_base, timestamp = robot.getImageBase()  # Mock bottom-mounted camera image
img_top, timestamp = robot.getImageTop()    # Mock top-mounted camera image
```

The mock API simulates network failures with a configurable failure rate. By default, there's a 1% chance that any mock API call will fail. You can adjust this rate:

```python
robot.failure_rate = 0.1  # Set 10% probability of command failure to mock network issues