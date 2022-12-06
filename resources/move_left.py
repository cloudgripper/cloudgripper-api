from flask_restful import Resource
from flask_jwt_extended import jwt_required

class MoveLeft(Resource):
    def __init__(self, **kwargs):
        self.robot = kwargs['robot']

    @jwt_required()
    def get(self):
        self.robot.step_left()
        return {"move": "left"}, 200