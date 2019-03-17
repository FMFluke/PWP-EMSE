from flask_restful import Resource
from flask import Response, request
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
"""-----Foodpoint.api does not exist yet!!-----"""
from Foodpoint.database import User
from Foodpoint.utils import MasonBuilder, create_error_response
from Foodpoint.utils import MASON, ERROR_PROFILE, USER_PROFILE, LINK_RELATIONS_URL
from Foodpoint.api import api
from Foodpoint import db
import json

"""
Class for constructing Mason document for Foodpoint related resource
"""
class FoodpointBuilder(MasonBuilder):

    @staticmethod
    def user_schema():
        schema = {
            "type": "object",
            "required": ["name", "userName"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of user",
            "type": "string"
        }
        props["userName"] =  {
            "description": "User unique identifer string",
            "type": "string"
        }
        return schema

    def add_control_all_users(self):
        self.add_control(
            "fpoint:all-users",
            href=api.url_for(AllUsers),
            title="All users"
        )

    def add_control_collections_by(self, user):
        self.add_control(
            "fpoint:collections-by",
            href=api.url_for(CollectionsByUser, user=user),
            title="Collections by this user"
        )

    def add_control_add_user(self):
        self.add_control(
            "fpoint:add-user",
            href=api.url_for(AllUsers),
            title="Add a new user",
            method="POST",
            encoding="json",
            schema=self.user_schema()
        )

    def add_control_all_categories(self):
        self.add_control(
            "fpoint:all-categories",
            href=api.url_for(AllCategories),
            title="All categories"
        )

    def add_control_all_ethnicities(self):
        self.add_control(
            "fpoint:all-ethnicities",
            href=api.url_for(AllEthnicities),
            title="All ethnicities"
        )

    def add_control_edit_user(self, user):
        self.add_control(
            "edit",
            href=api.url_for(EachUser, user=user),
            title="Edit this user's information",
            method="PUT",
            encoding="json",
            schema=self.user_schema()
        )

    def add_control_delete_user(self, user):
        self.add_control(
            "fpoint:delete",
            href=api.url_for(EachUser, user=user),
            title="Delete this user",
            method="DELETE"
        )

class AllUsers(Resource):

    def get(self):
        users = User.query.all()
        all_users = []
        for user in all_users:
            temp = FoodpointBuilder(
                name = user.name,
                userName = user.userName
            )
            temp.add_control("self", api.url_for(EachUser, user=user.userName))
            temp.add_control("profile", USER_PROFILE)
            all_users.append(temp)
        #create the response body, with the previous list as a field called 'items'
        body = FoodpointBuilder(
            items = all_users
        )
        body.add_namespace("fpoint", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(AllUsers))
        body.add_control_add_user()
        body.add_control_all_categories()
        body.add_control_all_ethnicities()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, FoodpointBuilder.user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        name = request.json["name"]
        userName = request.json["userName"])
        user = User(name=name, userName=userName)
        try:
            db.session.add(user)
            db.session.commit()
            return Response(status=204)
        except IntegrityError:
            db.session.rollback()
            return create_error_response(409, "Already exists", "User with userName {} already exists.".format(request.json["userName"]))

class EachUser(Resource):

    def get(self, user):
        target = User.query.filter_by(userName=user).first()
        if (target):
            body = FoodpointBuilder(
                name = target.name,
                userName = target.userName
            )
            body.add_namespace("fpoint", LINK_RELATIONS_URL)
            body.add_control("self", api.url_for(EachUser, user=target.userName))
            body.add_control("profile", USER_PROFILE)
            body.add_control_all_users()
            body.add_control_collections_by(target.userName)
            body.add_control_edit_user(target.userName)
            body.add_control_delete_user(target.userName)
            return Response(json.dumps(body), 200, mimetype=MASON)
        else:
            return create_error_response(404, "User not found")

    def put(self, user):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, FoodpointBuilder.user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        target = User.query.filter_by(userName=user).first()
        if (target):
            target.name = request.json["name"]
            target.userName = request.json["userName"])
            try:
                db.session.commit()
                return Response(status=204)
            except IntegrityError:
                db.session.rollback()
                return create_error_response(409, "Already exists", "User with userName {} already exists.".format(request.json["userName"]))
        else:
            return create_error_response(404, "User not found")

    def delete(self, user):
        target = User.query.filter_by(userName=user).first()
        if (target):
            db.session.delete(target)
            db.session.commit()
            return Response(status=204)
        else:
            return create_error_response(404, "User not found")

class CollectionsByUser(Resource):
    def get(self, user):
        pass

    def post(self, user):
        pass

class EachCollection(Resource):
    def get(self, user, col_name):
        pass

    def post(self, user, col_name):
        pass

    def put(self, user, col_name):
        pass

    def delete(self, user, col_name):
        pass

class AllCategories(Resource):
    def get(self):
        pass

    def post(self):
        pass

class EachCategory(Resource):
    def get(self, cat_name):
        pass

    def put(self, cat_name):
        pass

class AllEthnicities(Resource):
    def get(self):
        pass

    def post(self):
        pass

class EachEthnicity(Resource):
    def get(self, eth_name):
        pass

    def put(self, eth_name):
        pass

class EachRecipe(Resource):
    def get(self, user, col_name, recipe_id):
        pass

    def put(self, user, col_name, recipe_id):
        pass

    def delete(self, user, col_name, recipe_id):
        pass
