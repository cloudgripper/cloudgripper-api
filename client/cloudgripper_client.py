from requests import put, get, post, exceptions
import cv2
import time
import base64
import json
import struct
import numpy as np
import websocket

api_address_robots = {f"robot{i}": f"https://cloudgripper.eecs.kth.se:8443/robot{i}/api/v1.1/robot" for i in range(1, 33)}
api_address_robots_ws = {f"robot{i}": f"wss://cloudgripper.eecs.kth.se:8443/robot{i}/api/v1.1/robot" for i in range(1, 33)}

class GripperRobot:
    """
    A class to represent a CloudGripper robot

    Args:
        name (str): The name of the robot
        token (str): The token of the robot
    """
    global api_address_robots, api_address_robots_ws

    def __init__(self, name, token, jwt_token=""):
        self.name = name
        self.token = token
        self.jwt_token = jwt_token
        self.headers = {"apiKey": token}
        if jwt_token:
            self.headers["Authorization"] = f"Bearer {jwt_token}"
        self.base_api = api_address_robots[name]
        self.base_ws = api_address_robots_ws[name]
        self._ws = None

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

    def get_all_states(self):
        """
        Get the robot state and images from both cameras

        Args:
            None

        Returns:
            state (dict): current state of the robot
            time_state (float): timestamp of the state in seconds since the epoch
            image_base (numpy.ndarray): The base camera image as a numpy array
            time_base (float): timestamp of the base camera image in seconds since the epoch
            image_top (numpy.ndarray): The top camera image as a numpy array
            time_top (float): timestamp of the top camera image in seconds since the epoch
        """
        try:
            call_api = get(self.base_api + '/getAllStates',
                           headers=self.headers).json()

            image_base = base64.b64decode(call_api['data_base_camera'].encode('latin1'))
            npimg_base = np.frombuffer(image_base, dtype=np.uint8)
            source_base = cv2.imdecode(npimg_base, 1)

            image_top = base64.b64decode(call_api['data_top_camera'].encode('latin1'))
            npimg_top = np.frombuffer(image_top, dtype=np.uint8)
            source_top = cv2.imdecode(npimg_top, 1)

            return call_api['state'], call_api['time_state'], source_base, call_api['time_base_camera'], source_top, call_api['time_top_camera']
        except exceptions.RequestException as e:
            print('Request failed:', e)
            return None, None, None, None, None, None

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

    def step_action(self, action):
        """
        Execute a 5D robot action sequentially: x, y, z, rotation, grip

        Args:
            action (list): [x, y, z, rotation, grip], where x/y/z/grip are normalized and rotation is in degrees

        Returns:
            timestamp (float): Timestamp of the command in seconds since the epoch
        """
        if len(action) != 5:
            raise ValueError("action must contain [x, y, z, rotation, grip]")

        x, y, z, rotation, grip = action
        try:
            call_api = get(self.base_api + '/step/' + str(x) + '/' + str(y) + '/' + str(z) + '/' + str(rotation) + '/' + str(grip),
                           headers=self.headers).json()
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
            npimg = np.frombuffer(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return source, time_stamp
        except:
            print("Image not available")
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
            npimg = np.frombuffer(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return source, time_stamp
        except:
            print("Image not available")
            return None, None

    def connect_ws(self):
        """Open a persistent WebSocket connection to the robot."""
        url = self.base_ws + '/ws'
        if self.jwt_token:
            url += f'?token={self.jwt_token}'
        ws_headers = [f"apiKey: {self.token}", "Sec-WebSocket-Extensions: "]
        self._ws = websocket.create_connection(url, header=ws_headers, timeout=30)

    def disconnect_ws(self):
        """Close the persistent WebSocket connection."""
        if self._ws:
            self._ws.close()
            self._ws = None

    def __enter__(self):
        self.connect_ws()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect_ws()
        return False

    def _ensure_ws(self):
        if self._ws is None:
            self.connect_ws()

    def _ws_send(self, payload):
        self._ensure_ws()
        self._ws.send(json.dumps(payload))

    def _ws_recv_json(self):
        raw = self._ws.recv()
        data = json.loads(raw)
        if 'error' in data:
            raise RuntimeError(data['error'])
        return data

    def _ws_recv_binary(self):
        raw = self._ws.recv()
        meta_len = struct.unpack('>I', raw[:4])[0]
        meta = json.loads(raw[4:4 + meta_len])
        if 'error' in meta:
            raise RuntimeError(meta['error'])
        binary = raw[4 + meta_len:]
        return meta, binary

    def _decode_jpeg(self, jpeg_bytes):
        npimg = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        return cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    def get_state_ws(self):
        """Get the current robot state over WebSocket."""
        try:
            self._ws_send({'action': 'getState'})
            data = self._ws_recv_json()
            return data['state'], data['timestamp']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None, None

    def get_image_base_ws(self):
        """Get the base camera image over WebSocket."""
        try:
            self._ws_send({'action': 'getImageBase'})
            meta, jpeg_bytes = self._ws_recv_binary()
            return self._decode_jpeg(jpeg_bytes), meta['time']
        except Exception as e:
            print('WebSocket image not available:', e)
            return None, None

    def get_image_top_ws(self):
        """Get the top camera image over WebSocket."""
        try:
            self._ws_send({'action': 'getImageTop'})
            meta, jpeg_bytes = self._ws_recv_binary()
            return self._decode_jpeg(jpeg_bytes), meta['time']
        except Exception as e:
            print('WebSocket image not available:', e)
            return None, None

    def get_all_states_ws(self):
        """Get top image, base image, and robot state over WebSocket."""
        try:
            self._ws_send({'action': 'getAllStates'})
            meta, binary = self._ws_recv_binary()
            top_size = meta['top_image_size']
            top_img = self._decode_jpeg(binary[:top_size])
            base_img = self._decode_jpeg(binary[top_size:])
            timestamps = {
                'top': meta['time_top_camera'],
                'base': meta['time_base_camera'],
                'state': meta['time_state'],
            }
            return top_img, base_img, meta['state'], timestamps
        except Exception as e:
            print('WebSocket getAllStates failed:', e)
            return None, None, None, None

    def step_forward_ws(self):
        """Move the robot one step forward over WebSocket."""
        try:
            self._ws_send({'action': 'moveUp'})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def step_backward_ws(self):
        """Move the robot one step backward over WebSocket."""
        try:
            self._ws_send({'action': 'moveDown'})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def step_left_ws(self):
        """Move the robot one step left over WebSocket."""
        try:
            self._ws_send({'action': 'moveLeft'})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def step_right_ws(self):
        """Move the robot one step right over WebSocket."""
        try:
            self._ws_send({'action': 'moveRight'})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def move_xy_ws(self, x, y):
        """Move the robot to normalized x, y coordinates over WebSocket."""
        try:
            self._ws_send({'action': 'gcode', 'x': float(x), 'y': float(y)})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def move_gripper_ws(self, angle):
        """Move the gripper over WebSocket."""
        try:
            self._ws_send({'action': 'grip', 'grip_angle': angle})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def rotate_ws(self, angle):
        """Rotate the robot over WebSocket."""
        try:
            self._ws_send({'action': 'rotate', 'rotate_angle': int(angle)})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def move_z_ws(self, z):
        """Move the robot z-axis over WebSocket."""
        try:
            self._ws_send({'action': 'upDown', 'z_angle': z})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def step_action_ws(self, action):
        """Execute a 5D robot action over WebSocket."""
        if len(action) != 5:
            raise ValueError("action must contain [x, y, z, rotation, grip]")
        try:
            self._ws_send({'action': 'step', 'action_vector': action})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None

    def calibrate_ws(self):
        """Calibrate the robot over WebSocket."""
        try:
            self._ws_send({'action': 'calibrate'})
            return self._ws_recv_json()['time']
        except Exception as e:
            print('WebSocket request failed:', e)
            return None
