from Foodpoint import db
from Foodpoint.database import User, Recipe, Collection, Category, Ethnicity
import click
from flask.cli import with_appcontext
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy import event

#Enforce Foreign key, This function is adapted from Exercise 1
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def add_user(name, username):
    """
    Create a user instance and add into database
    Parameters:
    - name: String, name of user
    - username: String, string to identify user, this must be unique in the system otherwise adding to database will fail.
    Exception: Raise IntegrityError if username is not valid (not unique)
    """
    user = User(
        name=name,
        userName=username
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback() #recover database to be ready for new modification
        raise

def add_ethnicity(name):
    """
    Create an ethnicity instance and add into database
    Parameters:
    - name: String, name of ethnicity
    """
    ethnicity = Ethnicity(name=name)
    db.session.add(ethnicity)
    db.session.commit()

def add_category(name):
    """
    Create a category instance and add into database
    Parameters:
    - name: String, name of category
    """
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

def add_recipe(title, description, ingredients, ethnicity, category):
    """
    Create a category instance and add into database
    Parameters:
    - title: String, title of recipe
    - description: String, description of recipe
    - ingredients: String, ingredients in this recipe,
    - ethnicity: String, name of ethnicity, this must exist in Ethnicity table
    - category: String, name of category, this must exist in Category table
    Exception: Raise ValueError if ethnicity or category does not exist
               Raise IntegrityError if some field is not following restrictions (ex. exceeding max length or null when not allowed)
    """
    query_ethnicity = Ethnicity.query.filter_by(name=ethnicity).first()
    query_category = Category.query.filter_by(name=category).first()
    if query_category == None or query_ethnicity == None:
        raise ValueError("Foreign Key Ethnicity or Category does not exist.")
    recipe = Recipe(
        title=title,
        description=description,
        ingredients=ingredients,
        ethnicity = query_ethnicity,
        category=query_category
    )
    #db.session.add(recipe)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback() #recover database to be ready for new modification
        raise

def add_collection(name, user):
    """
    Create a category instance and add into database
    Parameters:
    - name: String, name of collection
    - user: String, username of user that own this collection, this must exist in User table
    Exception: Raise ValueError if user does not exist
               Raise IntegrityError if some field is not following restrictions (ex. exceeding max length or null when not allowed)
    """
    owner = User.query.filter_by(userName=user).first()
    if owner == None:
        raise ValueError("Foreign Key User does not exist.")
    collection = Collection(
        name=name,
        user=owner
    )
    #db.session.add(collection)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback() #recover database to be ready for new modification
        raise

def add_recipe_to_collection(recipeId, collectionId):
    """
    Add a recipe into a collection and commit the database (to populate RecipeCollection table)
    Parameters:
    - recipeId: id of recipe to add to collection, recipe with this id must exist in Recipe table
    - collectionId: id of collection to add recipe into, collection with this id must exist in Collection table
    Exception: Raise VauleError if recipe or collection with the id provided does not exist
    """
    collection = Collection.query.filter_by(id=collectionId).first()
    recipe = Recipe.query.filter_by(id=recipeId).first()
    if collection == None or recipe == None:
        raise ValueError("Collection or Recipe does not exist")
    collection.recipes.append(recipe)
    db.session.commit()

@click.command("populate-db")
@with_appcontext
def populate_database_example():
    """
    This function populate database with some example initial values, the database will be the one configured in the app
    and need to be created beforehand with command init-db. Note that here I did not catch exceptions because it
    is guaranteed to pass in this example, when adding custom instances it is best to catch exceptions,
    see possible exceptions from each function's definition
    """
    #add user
    add_user("Gordon Ramsey", "gdramsey")
    add_ethnicity("European")
    add_category("Seafood")
    add_collection("My Collection", "gdramsey")

    add_recipe(
        title="Salmon Steak",
        description="Fillet of salmon grilled with dill sauce, healthy and delicious",
        ingredients="Salmon fillet, yogurt, cream, dill",
        ethnicity="European",
        category="Seafood")
    salmon_id = Recipe.query.filter_by(title="Salmon Steak").first().id
    mycollection_id = Collection.query.filter_by(name="My Collection").first().id
    add_recipe_to_collection(salmon_id, mycollection_id)
