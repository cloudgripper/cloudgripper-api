from flask_restful import Resource
from flask_jwt_extended import jwt_required

class Gripper(Resource):
    def __init__(self, **kwargs):
        self.robot = kwargs['robot']

    @jwt_required()
    def get(self, grip_angle):
        self.robot.grip_open_close(int(grip_angle))
        return {"Pinch to ": grip_angle}, 200