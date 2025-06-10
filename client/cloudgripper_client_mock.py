import numpy as np
import time
import random
from requests import exceptions

api_address_robots = {f"robot{i}": f"https://cloudgripper.eecs.kth.se:8443/robot{i}/api/v1.1/robot" for i in range(1, 33)}

class GripperRobotMock:
    """
    A class to mock the CloudGripper class

    Args:
        name (str): The name of the robot
        token (str): The token of the robot
    """
    global api_address_robots

    def __init__(self, name, token):
        self.name = name
        self.headers = {"apiKey": token}
        self.base_api = api_address_robots[name]

        # Mock 1% probability of request failure
        self.failure_rate = 0.01

    def get_state(self):
        """
        Get the current state of the robot

        Args:
            None
        
        Returns:
            state (dict): current state of a mock robot:
                - 'x_norm': Normalized x-coordinate of the robot's position
                - 'y_norm': Normalized y-coordinate of the robot's position
                - 'z_norm': Normalized z-coordinate of the robot's position
                - 'rotation': Current rotation angle of the robot (in degrees)
                - 'claw_norm': Normalized state of the robot's gripper (0 for closed, 1 for open)
                - 'z_current': Current in the z-axis servo motor
                - 'rotation_current': Current in the rotation servo motor
                - 'claw_current': Current in the claw servo motor
            timestamp (float): timestamp of the state in seconds since the epoch
        """
        state = {'x_norm': 0.5, 
                 'y_norm': 0.5, 
                 'z_norm': 0.5, 
                 'rotation': 0,
                 'claw_norm': 0.5,
                 'z_current': 0,
                 'rotation_current': 0,
                 'claw_current': 0}
        
        timestamp = time.time()
        try:
            if random.random() > self.failure_rate:
                return state, timestamp
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None, None
        
    def step_forward(self):
        """
        Move the mock robot one step forward (y-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        
        try:
            if random.random() > self.failure_rate:
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def step_backward(self):
        """
        Move the mock robot one step backward (y-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        try:
            if random.random() > self.failure_rate:
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def step_left(self):
        """
        Move the mock robot one step left (x-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        try:
            if random.random() > self.failure_rate:
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def step_right(self):
        """
        Move the mock robot one step right (x-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        try:
            if random.random() > self.failure_rate:
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def move_gripper(self, angle):
        """
        Move the mock robot's gripper to the specified angle

        Args:
            angle (float): The desired angle for the gripper (0 for closed, 1 for open)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.gripperAngle = angle
        try:
            if random.random() > self.failure_rate:  
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def gripper_close(self):
        """
        Close the mock robot's gripper

        Args:
            None

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        time_stamp = self.move_gripper(0)
        return time_stamp

    def gripper_open(self):
        """
        Open the mock robot's gripper

        Args:
            None

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        time_stamp = self.move_gripper(1)
        return time_stamp

    def rotate(self, angle):
        """
        Rotate the mock robot to the specified angle

        Args:
            angle (float): The desired rotation angle for the robot (in degrees)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.rotationAngle = angle
        try:
            if random.random() > self.failure_rate:
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def move_z(self, z):
        """
        Move the mock robot's z-axis to the specified normalized position (z-direction)

        Args:
            z (float): The desired z-axis position for the robot (0 for fully down, 1 for fully up)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.zaxisAngle = z
        try:
            if random.random() > self.failure_rate:
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def move_xy(self, x, y):
        """
        Move the mock robot to the specified normalized x and y coordinates

        Args:
            x (float): The desired normalized x-coordinate for the robot (0 for leftmost, 1 for rightmost)
            y (float): The desired normalized y-coordinate for the robot (0 for backmost, 1 for forwardmost)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.robotPositionX = x
        self.robotPositionY = y
        try:
            if random.random() > self.failure_rate:
                return time.time()
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None
        
    def calibrate(self):
        """
        (INACTIVE) Calibrate the mock robot's position and orientation

        Args:
            None

        Returns:
            None
        """
        try:
            if random.random() > self.failure_rate:
                return
            else:
                raise exceptions.RequestException("Simulated request failure")
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def getImageBase(self):
        """
        Get the base camera image from the mock robot

        Args:
            None

        Returns:
            image (numpy.ndarray): The base camera image as a numpy array
            time_stamp (float): Timestamp of the image in seconds since the epoch
        """
        try:
            if random.random() > self.failure_rate:
                source = np.zeros((480, 640, 3), dtype=np.uint8)  # Create black image
                time_stamp = time.time()
                return source, time_stamp
            else:
                raise exceptions.RequestException("Simulated request failure")
        except:
            print("Image not available")
            return None, None

    def getImageTop(self):
        """
        Get the top camera image from the mock robot

        Args:
            None

        Returns:
            image (numpy.ndarray): The top camera image as a numpy array
            time_stamp (float): Timestamp of the image in seconds since the epoch
        """
        try:
            if random.random() > self.failure_rate:
                source = np.zeros((720, 1280, 3), dtype=np.uint8)  # Create black image
                time_stamp = time.time()
                return source, time_stamp
            else:
                raise exceptions.RequestException("Simulated request failure")
        except:
            print("Image not available")
            return None, None
