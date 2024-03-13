# CloudGripper Library: README

The CloudGripper API Client library provides a Python client to communicate with and control robotic arms over a cloud-based API. 

## Features

- Supports multiple robot instances.
- Simple functions to send commands and fetch robot state.
- Allows image fetching from robot cameras.

## Prerequisites

Before you start using the CloudGripper client library, ensure the following libraries are installed:

```bash
pip install -r requirements.txt
```

## Getting Started

1. **Setting up the Client**:

   First, ensure that your token for the CloudGripper API is set as an environment variable named `CLOUDGRIPPER_TOKEN`. Ensure you keep this token secure and do not share it publicly.

2. **Importing and Initializing the GripperRobot class**:

   Import the required libraries and classes.

   ```python
   from client.cloudgripper_client import GripperRobot
   import os
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
  - `robot.move_gripper(val)`# Adjusts the gripper's opening to a specific value, where 0 is fully close and 1 is fully open

- Fetch State and Image:
  - `robot.get_state()`
  - `robot.getImageBase()`
  - `robot.getImageTop()`

## Important Note

- Ensure you have a stable internet connection as the client communicates with the robots over the internet.

---
