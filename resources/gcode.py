from flask_restful import Resource
from flask_jwt_extended import jwt_required

class Gcode(Resource):
    def __init__(self, **kwargs):
        self.robot = kwargs['robot']

    @jwt_required()
    def get(self, x, y):
        self.robot.move_to(x,y)
        return {"gcode": "G00 X"+str(x)+" Y"+str(y)}, 200