import os
import pytest
import tempfile

import database
from database import User, Recipe, Collection, Category, Ethnicity
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event

#Enforce Foreign key, This function is adapted from Exercise 1
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

#All Python modules that either begin with test_ or end with _test are automatically detected by pytest.

@pytest.fixture
def db_handle():
    """
    This function setup a new database for testing. It is decorated with @pytest.fixture so it will run in
    every test that has this function's name as parameter

    This function is adapted from Exercise 1: Testing flask app part.
    """
    db_fd, db_fname = tempfile.mkstemp()
    database.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    database.app.config["TESTING"] = True

    with database.app.app_context():
        database.db.create_all()

    yield database.db

    os.close(db_fd)
    os.unlink(db_fname)

def _get_user():
    return User(
        name="John Doe",
        username="johndoe"
    )

def _get_recipe(choice=1):
    if choice == 1:
        return Recipe(
            title="Spaghetti Cabonara",
            description="Classic Italian dish blah blah",
            ingredients="spaghetti, egg, cheese, bacon"
        )
    else: #support only two options for now
        return Recipe(
            title="Chicken Marsala",
            description="I don't know",
            ingredients="chicken, tomato, something else"
        )

def _get_collection(number=1):
    return Collection(
        name="collection-{}".format(number)
    )

def _get_category(choice=1):
    if choice == 1:
        return Category(
            "name"="Pasta"
        )
    else:
        return Category(
            "name"="Curry"
        )

def _get_ethnicity(choice=1):
    if choice == 1:
        return Ethnicity(
            "name"="Italian"
        )
    else:
        return Ethnicity(
            "name"="Indian"
        )

def test_create_instances(db_handle):
    """
    Test: Add an instance of each class into database with all valid fields.
    Also test that we can find the instances in database after adding, and that all relationships work.
    """
    #create instances
    user = _get_user()
    ethnicity = _get_ethnicity()
    category = _get_category()
    collection = _get_collection()
    recipe = _get_recipe()
    recipe.category = category
    recipe.ethnicity = ethnicity
    collection.user = user
    collection.recipes.append(recipe)

    #add instances
    db_handle.session.add(user)
    db_handle.session.add(ethnicity)
    db_handle.session.add(category)
    db_handle.session.add(recipe)
    db_handle.session.add(collection)
    db_handle.session.commit()

    #check that everything is added
    assert User.query.count() == 1
    assert Recipe.query.count() == 1
    assert Collection.query.count() == 1
    assert Category.query.count() == 1
    assert Ethnicity.query.count() == 1
    db_user = User.query.first()
    db_recipe = Recipe.query.first()
    db_collection = Collection.query.first()
    db_category = Category.query.first()
    db_ethnicity = Ethnicity.query.first()

    #check relationship
    assert db_recipe.category == db_category
    assert db_recipe.ethnicity == db_ethnicity
    assert db_collection.user == db_user
    assert db_collection in db_user.collections
    assert db_recipe in db_collection.recipes
    assert db_collection in db_recipe.collections
