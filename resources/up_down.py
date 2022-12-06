from flask_restful import Resource
from flask_jwt_extended import jwt_required

class UpDown(Resource):
    def __init__(self, **kwargs):
        self.robot = kwargs['robot']

    @jwt_required()
    def get(self, z_angle):
        self.robot.grip_up_down(int(z_angle))
        return {"Up/Down to ": z_angle}, 200