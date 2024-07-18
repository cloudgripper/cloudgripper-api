import base64
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
from requests import exceptions, get


class GripperRobot:
    """
    A class to represent a gripper robot and interact with its API.

    Attributes:
        api_address_robots (dict): Dictionary mapping robot names to their API addresses.
        name (str): The name of the robot.
        headers (dict): The headers to be sent with each API request.
        base_api (str): The base API URL for the robot.
        order_count (int): Counter for the number of orders sent to the robot.
    """

    api_address_robots = {
        f"robot{i}": f"https://cloudgripper.zahidmhd.com/robot{i}/api/v1.1/robot"
        for i in range(1, 33)
    }

    def __init__(self, name: str, token: str):
        """
        Initialize the GripperRobot with a name and API token.

        Args:
            name (str): The name of the robot.
            token (str): The API token for authentication.
        """
        self.name = name
        self.headers = {"apiKey": token}
        self.base_api = self.api_address_robots[name]
        self.order_count = 0

    def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Make a GET request to the robot's API.

        Args:
            endpoint (str): The API endpoint to call.

        Returns:
            Optional[dict]: The JSON response from the API if successful, otherwise None.
        """
        try:
            response = get(f"{self.base_api}/{endpoint}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except exceptions.RequestException as e:
            print(f"Request to {endpoint} failed:", e)
            return None

    def _safe_get(self, response: Optional[Dict[str, Any]], key: str) -> Optional[Any]:
        """
        Safely get a value from the response dictionary.

        Args:
            response (Optional[dict]): The response dictionary.
            key (str): The key to retrieve the value for.

        Returns:
            Optional[Any]: The value if the key exists, otherwise None.
        """
        if response and key in response:
            return response[key]
        return None

    def get_state(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the current state of the robot.

        Returns:
            tuple: The state and timestamp of the robot.
        """
        response = self._make_request("getState")
        return self._safe_get(response, "state"), self._safe_get(response, "timestamp")

    def step_forward(self) -> Optional[str]:
        """
        Move the robot one step forward.

        Returns:
            Optional[str]: The time taken for the step.
        """
        response = self._make_request("moveUp")
        return self._safe_get(response, "time")

    def step_backward(self) -> Optional[str]:
        """
        Move the robot one step backward.

        Returns:
            Optional[str]: The time taken for the step.
        """
        response = self._make_request("moveDown")
        return self._safe_get(response, "time")

    def step_left(self) -> Optional[str]:
        """
        Move the robot one step to the left.

        Returns:
            Optional[str]: The time taken for the step.
        """
        response = self._make_request("moveLeft")
        return self._safe_get(response, "time")

    def step_right(self) -> Optional[str]:
        """
        Move the robot one step to the right.

        Returns:
            Optional[str]: The time taken for the step.
        """
        response = self._make_request("moveRight")
        return self._safe_get(response, "time")

    def move_gripper(self, angle: int) -> Optional[str]:
        """
        Move the robot's gripper to a specified angle.

        Args:
            angle (int): The angle to move the gripper to.

        Returns:
            Optional[str]: The time taken for the movement.
        """
        response = self._make_request(f"grip/{angle}")
        return self._safe_get(response, "time")

    def gripper_close(self) -> Optional[str]:
        """
        Close the robot's gripper.

        Returns:
            Optional[str]: The time taken for the movement.
        """
        return self.move_gripper(0)

    def gripper_open(self) -> Optional[str]:
        """
        Open the robot's gripper.

        Returns:
            Optional[str]: The time taken for the movement.
        """
        return self.move_gripper(1)

    def rotate(self, angle: int) -> Optional[str]:
        """
        Rotate the robot to a specified angle.

        Args:
            angle (int): The angle to rotate the robot to.

        Returns:
            Optional[str]: The time taken for the rotation.
        """
        response = self._make_request(f"rotate/{angle}")
        return self._safe_get(response, "time")

    def move_z(self, z: int) -> Optional[str]:
        """
        Move the robot along the Z-axis.

        Args:
            z (int): The distance to move along the Z-axis.

        Returns:
            Optional[str]: The time taken for the movement.
        """
        response = self._make_request(f"up_down/{z}")
        return self._safe_get(response, "time")

    def move_xy(self, x: int, y: int) -> Optional[str]:
        """
        Move the robot along the X and Y axes.

        Args:
            x (int): The distance to move along the X-axis.
            y (int): The distance to move along the Y-axis.

        Returns:
            Optional[str]: The time taken for the movement.
        """
        response = self._make_request(f"gcode/{x}/{y}")
        return self._safe_get(response, "time")

    def calibrate(self) -> None:
        """
        Calibrate the robot.
        """
        self._make_request("calibrate")

    def _decode_image(self, image_str: str) -> Optional[np.ndarray]:
        """
        Decode a base64-encoded image string into a numpy array.

        Args:
            image_str (str): The base64-encoded image string.

        Returns:
            Optional[np.ndarray]: The decoded image as a numpy array.
        """
        try:
            img_bytes = base64.b64decode(image_str.encode("latin1"))
            np_img = np.frombuffer(img_bytes, dtype=np.uint8)
            image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            print(f"Image decoding failed: {e}")
            return None

    def _get_image(
        self, endpoint: str
    ) -> Tuple[Optional[np.ndarray], Optional[str], Optional[str]]:
        """
        Retrieve an image from the robot's camera.

        Args:
            endpoint (str): The API endpoint to call for the image.

        Returns:
            Tuple[Optional[np.ndarray], Optional[str], Optional[str]]: The image as a numpy array, the timestamp, and the raw base64 image data.
        """
        response = self._make_request(endpoint)
        image_data = self._safe_get(response, "data")
        time_stamp = self._safe_get(response, "time")

        if image_data:
            image = self._decode_image(image_data)
            return image, time_stamp, image_data
        else:
            print("Image not available")
            return None, None, None

    def get_image_base(
        self,
    ) -> Tuple[Optional[np.ndarray], Optional[str], Optional[str]]:
        """
        Get the base image from the robot's camera.

        Returns:
            Tuple[Optional[np.ndarray], Optional[str], Optional[str]]: The image as a numpy array, the timestamp, and the raw base64 image data.
        """
        image, time_stamp, image_data = self._get_image("getImageBase")

        return image, time_stamp, image_data

    def get_image_top(self) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Get the top image from the robot's camera.

        Returns:
            Tuple[Optional[np.ndarray], Optional[str]]: The image as a numpy array and the timestamp.
        """
        img = self._get_image("getImageTop")

        return img[0], img[1]

    def get_all_states(
        self,
    ) -> Tuple[
        Optional[np.ndarray],
        Optional[np.ndarray],
        Optional[str],
        Optional[str],
    ]:
        """
        Get the combined state and images from the robot.

        Returns:
            Tuple[Optional[np.ndarray], Optional[str], Optional[np.ndarray], Optional[str], Optional[str], Optional[str]]:
                The top image, top image timestamp, base image, base image timestamp, robot state, and state timestamp.
        """
        response = self._make_request("getAllStates")
        if response is None:
            return None, None, None, None, None, None

        image_top_data = self._safe_get(response, "data_top_camera")
        time_top = self._safe_get(response, "time_top_camera")
        image_top = self._decode_image(image_top_data)

        image_base_data = self._safe_get(response, "data_base_camera")
        time_base = self._safe_get(response, "time_base_camera")
        image_base = self._decode_image(image_base_data)

        state = self._safe_get(response, "state")
        time_state = self._safe_get(response, "time_state")

        # Write the raw base64 data to files
        # if image_base_data:
        #     print("image base data type", type(image_base_data))
        #     with open("all_base_image_base64.txt", "w") as f:
        #         f.write(image_base_data)

        return image_top, image_base, state, time_state
