from flask_restful import Resource
from flask import Response, request
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from Foodpoint.database import User,Collection,Recipe,Category,Ethnicity
from Foodpoint.utils import MasonBuilder, create_error_response
from Foodpoint.utils import MASON, ERROR_PROFILE, USER_PROFILE, LINK_RELATIONS_URL, COLLECTION_PROFILE
from Foodpoint.utils import CATEGORY_PROFILE, ETHNICITY_PROFILE, RECIPE_PROFILE
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
        props["userName"] = {
            "description": "User unique identifer string",
            "type": "string"
        }
        return schema

    @staticmethod
    def collection_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of collection",
            "type": "string"
        }
        props["description"] = {
            "description": "Description for collection",
            "type": "string"
        }
        return schema

    @staticmethod
    def category_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of category",
            "type": "string"
        }
        props["description"] = {
            "description": "Description for category",
            "type": "string"
        }
        return schema

    @staticmethod
    def ethnicity_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of ethnicity",
            "type": "string"
        }
        props["description"] = {
            "description": "Description for ethnicity",
            "type": "string"
        }
        return schema

    @staticmethod
    def recipe_schema():
        schema = {
            "type": "object",
            "required": ["title", "description", "ingredients", "ethnicity", "category"]
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "title of recipe",
            "type": "string"
        }
        props["description"] = {
            "description": "recipe description",
            "type": "string"
        }
        props["ingredients"] = {
            "description": "ingredients of recipe",
            "type": "string"
        }
        props["rating"] = {
            "description": "rating of recipe",
            "type": "number"
        }
        props["ethnicity"] = {
            "description": "ethnicity of recipe",
            "type": "string"
        }
        props["category"] = {
            "description": "category of recipe",
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
            title="All Ethnicities"
        )

    def add_control_category(self,cat_name):
        self.add_control(
            "fpoint:category",
            href=api.url_for(EachCategory, cat_name=cat_name),
            title="Category of this recipe"
        )

    def add_control_ethnicity(self,eth_name):
        self.add_control(
            "fpoint:ethnicity",
            href=api.url_for(EachEthnicity, eth_name=eth_name),
            title="Ethnicity of this recipe"
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

    def add_control_add_collection(self, user):
        self.add_control(
            "fpoint:add-collection",
            href=api.url_for(CollectionsByUser, user=user),
            title="Add new collection for user",
            method="POST",
            encoding="json",
            schema=self.collection_schema()
        )

    def add_control_edit_collection(self, user, col_name):
        self.add_control(
            "edit",
            href=api.url_for(EachCollection, user=user, col_name=col_name),
            title="Edit this collection information",
            method="PUT",
            encoding="json",
            schema=self.collection_schema()
        )

    def add_control_edit_recipe(self, user, col_name, recipe_id):
        self.add_control(
            "edit",
            href=api.url_for(EachRecipe, user=user, col_name=col_name, recipe_id=recipe_id),
            title="Edit this recipe information",
            method="PUT",
            encoding="json",
            schema=self.recipe_schema()
        )

    def add_control_delete_collection(self, user, col_name):
        self.add_control(
            "fpoint:delete",
            href=api.url_for(EachCollection, user=user, col_name=col_name),
            title="Delete this collection",
            method="DELETE"
        )

    def add_control_delete_recipe(self, user, col_name, recipe_id):
        self.add_control(
            "fpoint:delete",
            href=api.url_for(EachRecipe, user=user, col_name=col_name, recipe_id=recipe_id),
            title="Delete this recipe",
            method="DELETE"
        )

    def add_control_add_recipe(self, user, col_name):
        self.add_control(
            "fpoint:add-recipe",
            href=api.url_for(EachCollection, user=user, col_name=col_name),
            title="Add new recipe to collection of user",
            method="POST",
            encoding="json",
            schema=self.recipe_schema()
        )

    def add_control_add_category(self):
        self.add_control(
            "fpoint:add-category",
            href=api.url_for(AllCategories),
            title="Add a new Category",
            method="POST",
            encoding="json",
            schema=self.category_schema()
        )

    def add_control_add_ethnicity(self):
        self.add_control(
            "fpoint:add-ethnicity",
            href=api.url_for(AllEthnicities),
            title="Add a new Ethnicity",
            method="POST",
            encoding="json",
            schema=self.ethnicity_schema()
        )

    def add_control_edit_category(self, cat_name):
        self.add_control(
            "edit",
            href=api.url_for(EachCategory, cat_name=cat_name),
            title="Edit this category's information",
            method="PUT",
            encoding="json",
            schema=self.category_schema()
        )

    def add_control_edit_ethnicity(self, eth_name):
        self.add_control(
            "edit",
            href=api.url_for(EachEthnicity, eth_name=eth_name),
            title="Edit this ethnicity's information",
            method="PUT",
            encoding="json",
            schema=self.ethnicity_schema()
        )

"""
Resouce classes for this api
"""
class AllUsers(Resource):

    def get(self):
        users = User.query.all()
        all_users = []
        for user in users:
            temp = FoodpointBuilder(
                name=user.name,
                userName=user.userName
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
        userName = request.json["userName"]
        user = User(name=name, userName=userName)
        try:
            db.session.add(user)
            db.session.commit()
            headers = {}
            headers["location"] = api.url_for(EachUser, user=userName)
            return Response("Success", 201, headers)
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
            target.userName = request.json["userName"]
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

#api.add_resource(CollectionsByUser, "/users/<user>/collections/")
class CollectionsByUser(Resource):
    def get(self, user):
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")

        userCollection = Collection.query.filter_by(userId=finduser.id)
        user_collection = []
        for collection in userCollection:
            temp = FoodpointBuilder(
                name=collection.name,
                description=collection.description
            )
            temp.add_control("self", api.url_for(EachCollection, user=user, col_name=collection.name))
            temp.add_control("profile", COLLECTION_PROFILE)
            user_collection.append(temp)
        #create the response body, with the previous list as a field called 'items'
        body = FoodpointBuilder(
            items=user_collection
        )
        body.add_namespace("fpoint", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(CollectionsByUser, user=user))
        body.add_control_add_collection(user)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, FoodpointBuilder.collection_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        name = request.json["name"]
        description = ""
        try:
            description = request.json["description"]
        except KeyError:
            pass
        collection = Collection(name=name, description=description, user=finduser)
        headers = {}
        headers["location"] = api.url_for(EachCollection, user=user, col_name=request.json["name"])
        try:
            db.session.add(collection)
            db.session.commit()
            return Response("Success", 201, headers)
        except IntegrityError:
            db.session.rollback()
            return create_error_response(409, "Already exists", "Collection against user {} already exists.".format(user))
#api.add_resource(EachCollection, "/users/<user>/collections/<col_name>/")
class EachCollection(Resource):
    def get(self, user, col_name):
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        findCol = Collection.query.filter_by(userId=finduser.id, name=col_name).first()
        if findCol is None:
            return create_error_response(404, "Collection not found")
        #query to be tested- get all recipes with collection name for user
        #col_recipes = Recipe.query.filter(Collection.collection.any(name=col_name)).all()
        col_recipes = findCol.recipes
        recipe_collection = []
        for collection in col_recipes:
            temp = FoodpointBuilder(
                title=collection.title,
                description=collection.description
            )
            temp.add_control("self", api.url_for(EachRecipe, user=user, col_name=col_name, recipe_id=collection.id))
            temp.add_control("profile", RECIPE_PROFILE)
            recipe_collection.append(temp)
        # create the response body, with the previous list as a field called 'items'
        body = FoodpointBuilder(
            items=recipe_collection
        )
        body.add_namespace("fpoint", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(EachCollection, user=user, col_name=col_name))
        body.add_control_collections_by(user)
        body.add_control_add_recipe(user, col_name)
        body.add_control_edit_collection(user, col_name)
        body.add_control_delete_collection(user, col_name)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user, col_name):
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        findCol = Collection.query.filter_by(userId=finduser.id, name=col_name).first()
        if findCol is None:
            return create_error_response(404, "Collection not found")
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")
        try:
            validate(request.json, FoodpointBuilder.recipe_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        findcategory = Category.query.filter_by(name=request.json["category"]).first()
        findethnicity = Ethnicity.query.filter_by(name=request.json["ethnicity"]).first()
        if findcategory is None:
            return create_error_response(404, "category not found")
        if findethnicity is None:
            return create_error_response(404, "ethnicity not found")

        title = request.json["title"]
        description = request.json["description"]
        ingredients = request.json["ingredients"]
        rating = ""
        try:
            rating = request.json["rating"]
        except KeyError:
            pass
        recipe = Recipe(title=title, description=description,ingredients=ingredients,rating=rating,category=findcategory,ethnicity=findethnicity)
        findCol.recipes.append(recipe)
        headers = {}

        db.session.commit()
        headers["location"] = api.url_for(EachRecipe, user=user, col_name=col_name, recipe_id=recipe.id)
        return Response("Success", 201, headers)

    def put(self, user, col_name):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")
        try:
            validate(request.json, FoodpointBuilder.collection_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        findCol = Collection.query.filter_by(userId=finduser.id, name=col_name).first()

        if (findCol):
            findCol.name = request.json["name"]
            try:
                findCol.description = request.json["description"]
            except KeyError:
                pass
            try:
                db.session.commit()
                return Response(status=204)
            except IntegrityError:
                db.session.rollback()
                return create_error_response(409, "Already exists", "Collection with name {} already exists for this user.".format(request.json["name"]))
        else:
            return create_error_response(404, "Collection not found")

    def delete(self, user, col_name):
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        target = Collection.query.filter_by(userId=finduser.id, name=col_name).first()
        if (target):
            db.session.delete(target)
            db.session.commit()
            return Response(status=204)
        else:
            return create_error_response(404, "Collection not found")
#api.add_resource(AllCategories, "/categories/")
class AllCategories(Resource):
    def get(self):
        categories = Category.query.all()
        all_categories = []
        for category in categories:
            temp = FoodpointBuilder(
                name=category.name,
                description=category.description
            )
            temp.add_control("self", api.url_for(EachCategory, cat_name=category.name))
            temp.add_control("profile", CATEGORY_PROFILE)
            all_categories.append(temp)
        # create the response body, with the previous list as a field called 'items'
        body = FoodpointBuilder(
            items=all_categories
        )
        body.add_namespace("fpoint", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(AllCategories))
        body.add_control_add_category()
        body.add_control_all_users()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, FoodpointBuilder.category_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        name = request.json["name"]
        description = ""
        try:
            description = request.json["description"]
        except KeyError:
            pass
        category = Category(name=name, description=description)
        try:
            db.session.add(category)
            db.session.commit()
            headers = {}
            headers["location"] = api.url_for(EachCategory, cat_name=name)
            return Response("Success", 201, headers)
        except IntegrityError:
            db.session.rollback()
            return create_error_response(409, "Already exists", "Category with name {} already exists.".format(request.json["name"]))


class EachCategory(Resource):
    def get(self, cat_name):
        target = Category.query.filter_by(name=cat_name).first()
        if (target):
            body = FoodpointBuilder(
                name=target.name,
                description=target.description
            )
            body.add_namespace("fpoint", LINK_RELATIONS_URL)
            body.add_control("self", api.url_for(EachCategory, cat_name=cat_name))
            body.add_control("profile", CATEGORY_PROFILE)
            body.add_control_all_categories()
            body.add_control_edit_category(cat_name)
            return Response(json.dumps(body), 200, mimetype=MASON)
        else:
            return create_error_response(404, "Category not found")

    def put(self, cat_name):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, FoodpointBuilder.category_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        target = Category.query.filter_by(name=cat_name).first()
        if (target):
            target.name = request.json["name"]
            try:
                target.description = request.json["description"]
            except KeyError:
                pass
            try:
                db.session.commit()
                return Response(status=204)
            except IntegrityError:
                db.session.rollback()
                return create_error_response(409, "Already exists", "Category with name {} already exists.".format(request.json["name"]))
        else:
            return create_error_response(404, "Category not found")


class AllEthnicities(Resource):
    def get(self):
        ethnicities = Ethnicity.query.all()
        all_ethnicities = []
        for ethnicity in ethnicities:
            temp = FoodpointBuilder(
                name=ethnicity.name,
                description=ethnicity.description
            )
            temp.add_control("self", api.url_for(EachEthnicity, eth_name=ethnicity.name))
            temp.add_control("profile", ETHNICITY_PROFILE)
            all_ethnicities.append(temp)
        # create the response body, with the previous list as a field called 'items'
        body = FoodpointBuilder(
            items=all_ethnicities
        )
        body.add_namespace("fpoint", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(AllEthnicities))
        body.add_control_all_users()
        body.add_control_add_ethnicity()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, FoodpointBuilder.ethnicity_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        name = request.json["name"]
        description = ""
        try:
            description = request.json["description"]
        except KeyError:
            pass
        ethnicity = Ethnicity(name=name, description=description)
        try:
            db.session.add(ethnicity)
            db.session.commit()
            headers = {}
            headers["location"] = api.url_for(EachEthnicity, eth_name=name)
            return Response("Success", 201, headers)
        except IntegrityError:
            db.session.rollback()
            return create_error_response(409, "Already exists", "Ethnicity with name {} already exists.".format(request.json["name"]))


class EachEthnicity(Resource):
    def get(self, eth_name):
        target = Ethnicity.query.filter_by(name=eth_name).first()
        if (target):
            body = FoodpointBuilder(
                name=target.name,
                description=target.description
            )
            body.add_namespace("fpoint", LINK_RELATIONS_URL)
            body.add_control("self", api.url_for(EachEthnicity, eth_name=eth_name))
            body.add_control("profile", ETHNICITY_PROFILE)
            body.add_control_all_ethnicities()
            body.add_control_edit_ethnicity(eth_name)
            return Response(json.dumps(body), 200, mimetype=MASON)
        else:
            return create_error_response(404, "Ethnicity not found")

    def put(self, eth_name):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, FoodpointBuilder.ethnicity_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        target = Ethnicity.query.filter_by(name=eth_name).first()
        if (target):
            target.name = request.json["name"]
            try:
                target.description = request.json["description"]
            except KeyError:
                pass
            try:
                db.session.commit()
                return Response(status=204)
            except IntegrityError:
                db.session.rollback()
                return create_error_response(409, "Already exists", "Ethnicity with name {} already exists.".format(request.json["name"]))
        else:
            return create_error_response(404, "Ethnicity not found")
#api.add_resource(EachRecipe, "/users/<user>/collections/<col_name>/<recipe_id>/")
class EachRecipe(Resource):
    def get(self, user, col_name, recipe_id):
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        findCol = Collection.query.filter_by(userId=finduser.id, name=col_name).first()
        if findCol is None:
            return create_error_response(404, "Collection not found")
        target = Recipe.query.filter_by(id=recipe_id).first()
        if target is None:
            return create_error_response(404, "Recipe not found")
        findEthnicity = Ethnicity.query.filter_by(id=target.ethnicityId).first()
        findCategory = Category.query.filter_by(id=target.categoryId).first()
        body = FoodpointBuilder(
                title=target.title,
                description=target.description,
                ingredients=target.ingredients,
                rating=target.rating,
                ethnicity=findEthnicity.name,
                category=findCategory.name
            )
        body.add_namespace("fpoint", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(EachRecipe, user=user, col_name=col_name, recipe_id=recipe_id))
        body.add_control("collection", RECIPE_PROFILE)
        body.add_control("profile", api.url_for(EachCollection, user=user,col_name=col_name))
        body.add_control_ethnicity(target.ethnicity)
        body.add_control_category(target.category)
        body.add_control_edit_recipe(user, col_name, recipe_id)
        body.add_control_delete_recipe(user, col_name, recipe_id)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, user, col_name, recipe_id):
        if (request.json == None):
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")
        try:
            validate(request.json, FoodpointBuilder.recipe_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        findCol = Collection.query.filter_by(userId=finduser.id, name=col_name).first()
        if findCol is None:
            return create_error_response(404, "Collection not found")
        findcategory = Category.query.filter_by(name=request.json["category"]).first()
        if findcategory is None:
            return create_error_response(404, "Category not found")
        findethnicity = Ethnicity.query.filter_by(name=request.json["ethnicity"]).first()
        if findethnicity is None:
            return create_error_response(404, "Ethnicity not found")
        target = Recipe.query.filter_by(id=recipe_id).first()
        if (target):
            try:
                target.rating = request.json["rating"]
            except KeyError:
                pass
            target.title = request.json["title"]
            target.description = request.json["description"]
            target.ingredients = request.json["ingredients"]
            target.category =findcategory
            target.ethnicity =findethnicity
            db.session.commit()
            return Response(status=204)
        else:
            return create_error_response(404, "Recipe not found")

    def delete(self, user, col_name, recipe_id):
        finduser = User.query.filter_by(userName=user).first()
        if finduser is None:
            return create_error_response(404, "User not found")
        findCol = Collection.query.filter_by(userId=finduser.id, name=col_name).first()
        if findCol is None:
            return create_error_response(404, "Collection not found")
        target = Recipe.query.filter_by(id=recipe_id).first()
        if (target):
            db.session.delete(target)
            db.session.commit()
            return Response(status=204)
        else:
            return create_error_response(404, "Recipe not found")
