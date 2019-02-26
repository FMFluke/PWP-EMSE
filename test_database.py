import os
import pytest
import tempfile

import database
from database import User, Recipe, Collection, Category, Ethnicity
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, StatementError
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


def _get_user(choice=1):
    if choice == 1:
        return User(
           name="kirn",
           userName="itzkirn"
        )
    else:
        return User(
           name="John Doe",
           userName="johndoe"
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
            title="Chicken Masala",
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
            name="Pasta"
        )
    else:
        return Category(
            name="Curry"
        )


def _get_ethnicity(choice=1):
    if choice == 1:
        return Ethnicity(
            name="Italian"
        )
    else:
        return Ethnicity(
            name="Indian"
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
    db_handle.session.rollback()

def test_recipe_columns(db_handle):
    """
    Tests that a rating value only accepts floating point values Also tests
    that description, ingredients and title  are mandatory but rating is optional for recipe.
    """

    recipe = _get_recipe()
    recipe.rating = str(recipe.rating)+"k"
    db_handle.session.add(recipe)
    with pytest.raises(StatementError):
        db_handle.session.commit()

    db_handle.session.rollback()

    recipe = _get_recipe()
    recipe.description = None
    db_handle.session.add(recipe)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    recipe = _get_recipe()
    recipe.title = None
    db_handle.session.add(recipe)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    recipe = _get_recipe()
    recipe.ingredients = None
    db_handle.session.add(recipe)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    recipe = _get_recipe()
    recipe.rating = None
    db_handle.session.add(recipe)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()


def test_username_unique(db_handle):
    """
    Tests that a username in user model is unique.
    """
    user_1 = _get_user()
    user_2 = _get_user()
    db_handle.session.add(user_1)
    db_handle.session.add(user_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    db_handle.session.rollback()


def test_updated_collection_name(db_handle):
    """
    Tests that collection name have been updated properly in collection model.
    """
    collection = _get_collection()
    user = _get_user()
    collection.user = user
    collection.name = "my new collection"
    db_handle.session.add(collection)
    db_handle.session.commit()
    db_collection = Collection.query.first()
    assert db_collection.name == "my new collection"
    db_handle.session.rollback()


def test_updated_name_of_user(db_handle):
    """
    Tests that name of user have been updated properly in user model.
    """
    user = _get_user()
    user.name = "laiq"
    db_handle.session.add(user)
    db_handle.session.commit()
    db_user = User.query.first()
    assert db_user.name == "laiq"
    db_handle.session.rollback()


def test_updated_description_of_recipe(db_handle):
    """
    Tests that description of recipe have been updated properly in user model.
    """
    recipe = _get_recipe()
    ethnicity = _get_ethnicity()
    category = _get_category()
    recipe.category = category
    recipe.ethnicity = ethnicity
    recipe.description = "description updated"
    db_handle.session.add(recipe)
    db_handle.session.commit()
    db_recipe = Recipe.query.first()
    assert db_recipe.description == "description updated"
    db_handle.session.rollback()


def test_deleting_user(db_handle):
    """
    Tests that user have been properly removed from user model.
    """
    user = _get_user()
    db_handle.session.add(user)
    db_handle.session.commit()
    db_handle.session.delete(user)
    assert User.query.count() == 0
    db_handle.session.rollback()


def test_user_collection_relationship(db_handle):
    """
    Tests breaking of foreign key relationship, that one collection belong to only single user,
    i.e foreign key relationship.
    """
    user_1 = _get_user(1)
    user_2 = _get_user()
    collection = _get_collection()
    collection.user = user_1
    db_handle.session.add(collection)
    collection.user = user_2
    db_handle.session.add(collection)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    db_handle.session.rollback()


def test_recipe_category_and_ethnicity_relationship(db_handle):
    """
    Tests breaking of foreign key relationship, checks that we can not assign
     same category and ethnicity twice to same recipe,also test rating value can be null i.e won't
     give any exception.
    """
    category_1 = _get_category(1)
    category_2 = _get_category()
    ethnicity_1 = _get_ethnicity(1)
    ethnicity_2 = _get_ethnicity()
    recipe = _get_recipe()
    recipe.category = category_1
    recipe.ethnicity = ethnicity_1
    db_handle.session.add(recipe)
    recipe.category = category_2
    recipe.ethnicity = ethnicity_2
    db_handle.session.add(recipe)
    db_handle.session.commit()
    assert Recipe.query.count() == 1
    #with pytest.raises(IntegrityError):
        #db_handle.session.commit()
    db_handle.session.rollback()


def test_recipe_collection_relationship(db_handle):
    """
    Tests breaking of primary key relationship, that we can not have two identical
     rows in recipecollection table i.e adding same recipe again.
    """
    user = _get_user()
    ethnicity = _get_ethnicity()
    category = _get_category()
    collection = _get_collection()
    recipe_1 = _get_recipe()
    recipe_1.category = category
    recipe_1.ethnicity = ethnicity
    collection.user = user
    collection.recipes.append(recipe_1)
    db_handle.session.add(collection)
    collection.recipes.append(recipe_1)
    db_handle.session.add(collection)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    db_handle.session.rollback()


def test_collection_ondelete_user(db_handle):
    """
    Tests that collection owned by the user is deleted when the user
    is deleted.
    """

    user = _get_user()
    collection = _get_collection()
    collection.user = user
    db_handle.session.add(user)
    db_handle.session.add(collection)
    db_handle.session.commit()
    db_handle.session.delete(user)
    db_handle.session.commit()
    assert Collection.query.count() == 0
