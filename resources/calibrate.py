from flask_restful import Resource
from flask_jwt_extended import jwt_required

class Calibrate(Resource):
    def __init__(self, **kwargs):
        self.robot = kwargs['robot']

    @jwt_required()
    def get(self):
        self.robot.calibrate()
        return {"Action": "Calibrate"}, 200