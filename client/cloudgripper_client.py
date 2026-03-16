from requests import put, get, post, exceptions
import cv2
import time
import base64
import numpy as np

api_address_robots = {f"robot{i}": f"https://cloudgripper.eecs.kth.se:8443/robot{i}/api/v1.1/robot" for i in range(1, 33)}
api_address_eval = {f"robot{i}": f"https://cloudgripper.eecs.kth.se:8443/robot{i}/api/v1.1/eval" for i in range(1, 33)}

class GripperRobot:
    """
    A class to represent a CloudGripper robot

    Args:
        name (str): The name of the robot
        token (str): The token of the robot
    """
    global api_address_robots, api_address_eval

    def __init__(self, name, token):
        self.name = name
        self.headers = {"apiKey": token}
        self.base_api = api_address_robots[name]
        self.eval_api = api_address_eval[name]

    def get_state(self):
        """
        Get the current state of the robot

        Args:
            None
        
        Returns:
            state (dict): current state of the robot:
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
        try:
            call_api = get(self.base_api + '/getState',
                           headers=self.headers).json()
            return call_api['state'], call_api['timestamp']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None, None

    def step_forward(self):
        """
        Move the robot one step forward (y-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        try:
            call_api = get(self.base_api + '/moveUp',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def step_backward(self):
        """
        Move the robot one step backward (y-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        try:
            call_api = get(self.base_api + '/moveDown',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None
        
    def step_left(self):
        """
        Move the robot one step left (x-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        try:
            call_api = get(self.base_api + '/moveLeft',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None
        
    def step_right(self):
        """
        Move the robot one step right (x-direction)

        Args:
            None

        Returns:
            timestamp (float): timestamp of the command in seconds since the epoch
        """
        try:
            call_api = get(self.base_api + '/moveRight',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def move_gripper(self, angle):
        """
        Move the robot's gripper to the specified angle

        Args:
            angle (float): The desired angle for the gripper (0 for closed, 1 for open)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.gripperAngle = angle
        try:
            call_api = get(self.base_api + '/grip/' + str(self.gripperAngle),
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def gripper_close(self):
        """
        Close the robot's gripper

        Args:
            None

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        time_stamp = self.move_gripper(0)
        return time_stamp

    def gripper_open(self):
        """
        Open the robot's gripper

        Args:
            None

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        time_stamp = self.move_gripper(1)
        return time_stamp

    def rotate(self, angle):
        """
        Rotate the robot to the specified angle

        Args:
            angle (float): The desired rotation angle for the robot (in degrees)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.rotationAngle = angle
        try:
            call_api = get(self.base_api + '/rotate/' +
                           str(angle), headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def move_z(self, z):
        """
        Move the robot's z-axis to the specified normalized position (z-direction)

        Args:
            z (float): The desired z-axis position for the robot (0 for fully down, 1 for fully up)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.zaxisAngle = z
        try:
            call_api = get(self.base_api + '/up_down/' +
                           str(z), headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def move_xy(self, x, y):
        """
        Move the robot to the specified normalized x and y coordinates

        Args:
            x (float): The desired normalized x-coordinate for the robot (0 for leftmost, 1 for rightmost)
            y (float): The desired normalized y-coordinate for the robot (0 for backmost, 1 for forwardmost)

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        self.robotPositionX = x
        self.robotPositionY = y
        try:
            call_api = get(self.base_api + '/gcode/' + str(x) +
                           '/' + str(y), headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def calibrate(self):
        """
        (INACTIVE) Calibrate the robot's position and orientation

        Args:
            None

        Returns:
            None
        """
        try:
            get(self.base_api +
                '/calibrate', headers=self.headers).json()
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def getImageBase(self):
        """
        Get the base camera image from the robot

        Args:
            None

        Returns:
            image (numpy.ndarray): The base camera image as a numpy array
            time_stamp (float): Timestamp of the image in seconds since the epoch
        """
        try:
            call_api = get(
                self.base_api+'/getImageBase', headers=self.headers).json()
            getimage = call_api['data']
            time_stamp = call_api['time']
            encode_img = getimage.encode('latin1')
            img = base64.b64decode(encode_img)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return source, time_stamp
        except:
            print("Image not available")
            return None, None

    def getImageBaseUndistorted(self):
        """
        Get undistoted base camera image
        
        Args:
            None

        Returns:
            image (numpy.ndarray): Undistorted base camera frame as a numpy array
            time_stamp (float): Timestamp of the image in seconds since the epoch
        """
        try:
            call_api = get(
                self.base_api + '/getImageBaseUndistorted', headers=self.headers).json()
            getimage = call_api['data']
            time_stamp = call_api['time']
            encode_img = getimage.encode('latin1')
            img = base64.b64decode(encode_img)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return source, time_stamp
        except:
            print("Undistorted image not available")
            return None, None

    def getImageTop(self):
        """
        Get the top camera image from the robot

        Args:
            None

        Returns:
            image (numpy.ndarray): The top camera image as a numpy array
            time_stamp (float): Timestamp of the image in seconds since the epoch
        """
        try:
            call_api = get(
                self.base_api+'/getImageTop', headers=self.headers).json()
            getimage = call_api['data']
            time_stamp = call_api['time']
            encode_img = getimage.encode('latin1')
            img = base64.b64decode(encode_img)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return source, time_stamp
        except:
            print("Image not available")
            return None, None

    # ------------------------------------------------------------------
    # Evaluation endpoints
    # ------------------------------------------------------------------

    def eval_start(self):
        """
        Start an evaluation run.  180s evaluation time starts and background IoU tracking begins.

        Returns:
            result (dict | None): On success:
                - 'status': "Evaluation initialized"
                - 'max_duration_seconds': 180
                - 'system_time_start': server-side UNIX timestamp
              On failure returns None.
        """
        try:
            resp = get(self.eval_api + '/start', headers=self.headers)
            data = resp.json()
            if resp.status_code != 200:
                print(f"eval_start failed: {data.get('error', data)}")
                return None
            return data
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def eval_target(self):
        """
        Retrieve the target geometry for the current evaluation run.
        Coordinates are in undistorted 2D pixel space.

        Returns:
            result (dict | None): On success:
                - 'task': e.g. "planar_pushing"
                - 'target_object': e.g. "square", "circle", "t"
                - 'coordinate_space': "undistorted_pixel_2d"
                - 'geometry': {"type": "polygon", "points": [{"x": ..., "y": ...}, ...]}
              On failure returns None.
        """
        try:
            resp = get(self.eval_api + '/target', headers=self.headers)
            data = resp.json()
            if resp.status_code != 200:
                print(f"eval_target failed: {data.get('error', data)}")
                return None
            return data
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None

    def eval_status(self):
        """
        Get the current evaluation status.

        Returns:
            result (dict | None): On success, one of:
              While running:
                - 'status': "running"
                - 'time_elapsed': float (seconds)
                - 'time_remaining': float (seconds)
                - 'current_iou': float
              When completed:
                - 'status': "completed"
                - 'final_score': float (integral of IoU over time)
                - 'iou_history': [{"t": float, "iou": float}, ...]
                - 'message': str
              While resetting:
                - 'status': "resetting"
                - 'message': str
              On failure returns None.
        """
        try:
            resp = get(self.eval_api + '/status', headers=self.headers)
            data = resp.json()
            if resp.status_code != 200:
                print(f"eval_status failed: {data.get('error', data)}")
                return None
            return data
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None