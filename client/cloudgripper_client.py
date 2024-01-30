from requests import put, get, post, exceptions
import cv2
import base64
import numpy as np

api_address_robots = {f"robot{i}": f"https://cloudgripper.zahidmhd.com/robot{i}/api/v1.1/robot" for i in range(1, 33)}

class GripperRobot:
    global api_address_robots

    def __init__(self, name, token):
        self.name = name
        self.headers = {"apiKey": token}
        self.base_api = api_address_robots[name]

    def get_state(self):
        try:
            call_api = get(self.base_api + '/state',
                           headers=self.headers).json()
            return call_api['state'], call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def step_forward(self):
        try:
            call_api = get(self.base_api + '/moveUp',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def step_backward(self):
        try:
            call_api = get(self.base_api + '/moveDown',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def step_left(self):
        try:
            call_api = get(self.base_api + '/moveLeft',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def step_right(self):
        try:
            call_api = get(self.base_api + '/moveRight',
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def move_gripper(self, angle):
        self.gripperAngle = angle
        try:
            call_api = get(self.base_api + '/grip/' + str(self.gripperAngle),
                           headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def gripper_close(self):
        time_stamp = self.move_gripper(90)
        return time_stamp

    def gripper_open(self):
        time_stamp = self.move_gripper(40)
        return time_stamp

    def rotate(self, angle):
        self.rotationAngle = angle

        sendAngle = -angle + 180
        try:
            call_api = get(self.base_api + '/rotate/' +
                           str(sendAngle), headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def move_z(self, z):
        self.zaxisAngle = z
        calcVal = (-180/1)*z + 180
        calcVal = int(calcVal)
        try:
            call_api = get(self.base_api + '/up_down/' +
                           str(calcVal), headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def move_xy(self, x, y):
        self.robotPositionX = x
        self.robotPositionY = y

        x_send = 125*x + 15
        y_send = 130*y + 30
        try:
            call_api = get(self.base_api + '/gcode/' + str(x_send) +
                           '/' + str(y_send), headers=self.headers).json()
            return call_api['time']
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def calibrate(self):
        try:
            get(self.base_api +
                '/calibrate', headers=self.headers).json()
        except exceptions.RequestException as e:
            print('Request failed:', e)

    def getImage(self):
        try:
            call_api = get(
                self.base_api+'/getImage', headers=self.headers).json()
            getimage = call_api['data']
            time_stamp = call_api['time']
            encode_img = getimage.encode('latin1')
            img = base64.b64decode(encode_img)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return source, time_stamp
        except:
            print("Image not available")

    def getImageTop(self):
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
