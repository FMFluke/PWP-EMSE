from flask import Blueprint, Response
from flask_restful import Resource, Api
api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports
from Foodpoint.resources import AllUsers, EachUser

#add route to each resources
api.add_resource(AllUsers, "/users/")
api.add_resource(EachUser, "/users/<user>/")
api.add_resource(CollectionsByUser, "/users/<user>/collections/")
api.add_resource(EachCollection, "/users/<user>/collections/<col_name>/")
api.add_resource(EachRecipe, "/users/<user>/collections/<col_name>/<recipe_id>/")
api.add_resource(AllCategories, "/categories/")
api.add_resource(EachCategory, "/categories/<cat_name>/")
api.add_resource(AllEthnicities, "/ethnicities/")
api.add_resource(EachEthnicity, "/ethnicities/<eth_name>/")

@api_bp.route("/")
def entry_point():
    return 404 #placeholder
