from flask import Flask, request
from flask_restful import Resource
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

        
class Login(Resource):
    def __init__(self, **kwargs):
        self.users = kwargs['users']
        self.app = kwargs['app']

    def post(self):
        email = request.form["email"]
        password = request.form["password"]
        test = self.users.find_one({"email": email, "password": password})
        if test:
            with self.app.app_context():
                access_token = create_access_token(identity=email)
                print("---------------------------------")
                print(create_access_token(identity=email))
                print("---------------------------------")
            return {'access token ': access_token, 'message':'Login Succeeded'}, 200
        else:
            return {'Message':'Bad credentials'}, 401
