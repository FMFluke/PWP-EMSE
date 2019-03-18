import os
import pytest
import tempfile

from Foodpoint import create_app, db
from Foodpoint.database import User, Recipe, Collection, Category, Ethnicity
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy import event

#All Python modules that either begin with test_ or end with _test are automatically detected by pytest.

@pytest.fixture
def app():
    """
    This function setup a new app for testing using test configuration. It is decorated with @pytest.fixture
    so it will run in every test that has this function's name as parameter

    This function is adapted from Exercise 1: Testing flask app part and Exercise 3 Project layout part.
    """
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI" : "sqlite:///" + db_fname,
        "TESTING" : True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app

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

def test_create_instances(app):
    """
    Test: Add an instance of each class into database with all valid fields.
    Also test that we can find the instances in database after adding, and that all relationships work.
    """
    with app.app_context():
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
        db.session.add(user)
        db.session.add(ethnicity)
        db.session.add(category)
        db.session.add(recipe)
        db.session.add(collection)
        db.session.commit()

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
        db.session.rollback()

def test_recipe_columns(app):
    """
    Tests that a rating value only accepts floating point values Also tests
    that description, ingredients and title  are mandatory but rating is optional for recipe.
    """
    with app.app_context():
        recipe = _get_recipe()
        recipe.rating = str(recipe.rating)+"k"
        db.session.add(recipe)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

        recipe = _get_recipe()
        recipe.description = None
        db.session.add(recipe)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        recipe = _get_recipe()
        recipe.title = None
        db.session.add(recipe)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        recipe = _get_recipe()
        recipe.ingredients = None
        db.session.add(recipe)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        recipe = _get_recipe()
        recipe.rating = None
        db.session.add(recipe)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


def test_username_unique(app):
    """
    Tests that a username in user model is unique.
    """
    with app.app_context():
        user_1 = _get_user()
        user_2 = _get_user()
        db.session.add(user_1)
        db.session.add(user_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_updated_collection_name(app):
    """
    Tests that collection name have been updated properly in collection model.
    """
    with app.app_context():
        collection = _get_collection()
        user = _get_user()
        collection.user = user
        collection.name = "my new collection"
        db.session.add(collection)
        db.session.commit()
        db_collection = Collection.query.first()
        assert db_collection.name == "my new collection"
        db.session.rollback()


def test_updated_name_of_user(app):
    """
    Tests that name of user have been updated properly in user model.
    """
    with app.app_context():
        user = _get_user()
        user.name = "laiq"
        db.session.add(user)
        db.session.commit()
        db_user = User.query.first()
        assert db_user.name == "laiq"
        db.session.rollback()


def test_updated_description_of_recipe(app):
    """
    Tests that description of recipe have been updated properly in user model.
    """
    with app.app_context():
        recipe = _get_recipe()
        ethnicity = _get_ethnicity()
        category = _get_category()
        recipe.category = category
        recipe.ethnicity = ethnicity
        recipe.description = "description updated"
        db.session.add(recipe)
        db.session.commit()
        db_recipe = Recipe.query.first()
        assert db_recipe.description == "description updated"
        db.session.rollback()


def test_deleting_user(app):
    """
    Tests that user have been properly removed from user model.
    """
    with app.app_context():
        user = _get_user()
        db.session.add(user)
        db.session.commit()
        db.session.delete(user)
        assert User.query.count() == 0
        db.session.rollback()


def test_user_collection_relationship(app):
    """
    Tests breaking of foreign key relationship, that one collection must belong to an existing user.
    """
    with app.app_context():
        user = _get_user(1)
        collection = _get_collection()
        collection.user = user
        db.session.add(collection)
        db.session.commit()
        collection = Collection.query.first()
        collection.userId = collection.userId + 202 #does not exist
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_recipe_category_and_ethnicity_relationship(app):
    """
    Tests breaking of foreign key relationship, checks that we can not assign
     non existing category and ethnicity to a recipe.
    """
    with app.app_context():
        category_1 = _get_category(1)
        ethnicity_1 = _get_ethnicity(1)
        recipe = _get_recipe()
        recipe.category = category_1
        recipe.ethnicity = ethnicity_1
        db.session.add(recipe)
        db.session.commit()
        assert Recipe.query.count() == 1

        recipe = Recipe.query.first()
        recipe.ethnicityId = recipe.ethnicityId + 131 #does not exist
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        recipe = Recipe.query.first()
        recipe.categoryId = recipe.categoryId + 131 #does not exist
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()



def test_recipe_collection_relationship(app):
    """
    Tests breaking of primary key relationship, that we can not have two identical
     rows in recipecollection table i.e adding same recipe again.
    """
    with app.app_context():
        user = _get_user()
        ethnicity = _get_ethnicity()
        category = _get_category()
        collection = _get_collection()
        recipe_1 = _get_recipe()
        recipe_1.category = category
        recipe_1.ethnicity = ethnicity
        collection.user = user
        collection.recipes.append(recipe_1)
        collection.recipes.append(recipe_1)
        db.session.add(collection)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_collection_ondelete_user(app):
    """
    Tests that collection owned by the user is deleted when the user
    is deleted.
    """
    with app.app_context():
        user = _get_user()
        collection = _get_collection()
        collection.user = user
        db.session.add(user)
        db.session.add(collection)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        assert Collection.query.count() == 0


def test_constraint_collection_name(app):
    """
    Test that a user can't have two collections with the same name.
    """
    with app.app_context():
        collection_1 = _get_collection()
        collection_2 = _get_collection()
        user = _get_user()
        collection_1.user = user
        collection_2.user = user
        db.session.add(user)
        db.session.add(collection_1)
        db.session.add(collection_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
