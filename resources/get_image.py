from flask_restful import Resource
from flask_jwt_extended import jwt_required
import cv2
import os
import base64

class GetImage(Resource):
    def __init__(self, **kwargs):
        self.robot = kwargs['robot']

    @jwt_required()
    def get(self):
        frame = self.robot.get_image()
        encoded, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        image_str = jpg_as_text.decode('latin1')
        return {'data': image_str}, 200