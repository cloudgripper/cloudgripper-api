from flask import Flask, request
from flask_restful import Resource
        
class Register(Resource):
    def __init__(self, **kwargs):
        self.users = kwargs['users']

    def post(self):
        email = request.form["email"]
        test = self.users.find_one({"email": email})
        if test:
            return {'Message':'User already exists'}, 409
        else:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            password = request.form["password"]
            user_info = dict(first_name=first_name, last_name=last_name, email=email, password=password)
            self.users.insert_one(user_info)
            return {'message':"User added sucessfully"}, 201