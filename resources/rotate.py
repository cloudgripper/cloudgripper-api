from flask_restful import Resource
from flask_jwt_extended import jwt_required

class Rotate(Resource):
    def __init__(self, **kwargs):
        self.robot = kwargs['robot']

    @jwt_required()
    def get(self, rotate_angle):
        self.robot.rotate(int(rotate_angle))
        return {"Rotate to ": rotate_angle}, 200