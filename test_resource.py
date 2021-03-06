import os
import pytest
import tempfile
import json

from Foodpoint import create_app, db
from Foodpoint.database import User, Recipe, Collection, Category, Ethnicity
from sqlalchemy.exc import IntegrityError, StatementError
from jsonschema import validate

#All Python modules that either begin with test_ or end with _test are automatically detected by pytest.

@pytest.fixture
def client():
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
        _populate_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    """
    Pre-populate database with 3 users each with one collection which contains one recipe.
    """
    for i in range(1,4):
        user = User(name="User Name{}".format(i),
                    userName="user-{}".format(i)
                )
        db.session.add(user)
        category = Category(name="category{}".format(i))
        ethnicity = Ethnicity(name="ethnicity{}".format(i))
        db.session.add(ethnicity)
        db.session.add(category)
        for j in range(1,3):
            collection = Collection(name="Collection{}-of-User{}".format(j, i))
            collection.user = user
            for k in range(1,3):
                recipe = Recipe(title="test-col{}-recipe{}".format(j, k),
                                description="description",
                                ingredients="ingredients"
                            )
                recipe.category = category
                recipe.ethnicity = ethnicity
                collection.recipes.append(recipe)
                db.session.add(recipe)
            db.session.add(collection)
    db.session.commit()

def _check_namespace(client, response):
    """
    Checks that the "fpoint" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.

    This function is adapted from example in exercise 3 testing part.
    """

    ns_href = response["@namespaces"]["fpoint"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 302

def _check_profile_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed
    specially created for profile.

    This function is adapted from example in exercise 3 testing part.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 302

def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.

    This function is adapted from example in exercise 3 testing part.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

def _check_control_post_method(ctrl, client, body, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.

    This function is adapted from example in exercise 3 testing part.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

def _check_control_put_method(ctrl, client, body, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.

    This function is adapted from example in exercise 3 testing part.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    #body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204

def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.

    This function is adapted from example in exercise 3 testing part.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

def _get_user_json(number=1):
    """
    Generate valid json document for PUT and POST test of User resource
    """
    return {"name": "Extra Testname{}".format(number), "userName": "extratestname{}".format(number)}

def _get_collection_json(number=1):
    """
    Generate valid json document for PUT and POST test of Collection resource
    """
    return {"name": "Test-Collection-{}".format(number)}

def _get_recipe_json(number=1):
    """
    Generate valid json document for PUT and POST test of Recipe resource
    Use in this document existing category and ethnicity added in _populate_db()
    """
    return {"title": "Extra-Recipe-{}".format(number),
            "description": "Test description",
            "ingredients": "Test ingredients",
            "ethnicity": "ethnicity1",
            "category": "category1"}

def _get_category_json(number=1):
    """
    Generate valid json document for PUT and POST test of Category resource
    """
    return {"name": "Test-Category-{}".format(number)}

def _get_ethnicity_json(number=1):
    """
    Generate valid json document for PUT and POST test of Ethnicity resource
    """
    return {"name": "Test-Ethnicity-{}".format(number)}

class TestAllUsers(object):
    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        """Tests for AllUsers GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 3
        _check_namespace(client, body)
        _check_control_post_method("fpoint:add-user", client, _get_user_json(), body)
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile_get_method("profile", client, item)
            assert "name" in item
            assert "userName" in item

    def test_post(self, client):
        """Tests for AllUsers POST method"""
        valid = _get_user_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["userName"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Extra Testname1"
        assert body["userName"] == "extratestname1"

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        # test with already exists userName
        valid["userName"] = "user-1"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        #remove field 'name' so document become invalid
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestUser(object):
    RESOURCE_URL = "/api/users/user-1/"
    INVALID_URL = "/api/users/non-exist/"
    MODIFIED_URL = "/api/users/extratestname1/"

    def test_get(self, client):
        """Tests for User GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "User Name1"
        assert body["userName"] == "user-1"
        _check_namespace(client, body)
        _check_profile_get_method("profile", client, body)
        _check_control_get_method("fpoint:all-users", client, body)
        _check_control_get_method("fpoint:collections-by", client, body)
        #we don't want to change the unique userName when testing PUT otherwise we can't test delete because URL will be changed
        valid = _get_user_json()
        valid["userName"] = body["userName"]
        _check_control_put_method("edit", client, valid, body)
        _check_control_delete_method("fpoint:delete", client, body)

        #user not exist
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """Tests for User PUT method"""
        valid = _get_user_json()

        #test valid but don't change userName
        valid["userName"] = "user-1"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        #test wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test user not exist
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        #test duplicate userName
        valid["userName"] = "user-2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #test invalid document, missing userName
        valid.pop("userName")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #test valid with changed URL
        valid = _get_user_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]

    def test_delete(self, client):
        """Tests for User DELETE method"""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestCollectionsByUser(object):

    RESOURCE_URL = "/api/users/user-1/collections/"
    INVALID_URL = "/api/users/not-user/collections/"

    def test_get(self, client):
        """Tests for CollectionsByUser GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #in _populate_db we added two collections for each user
        assert len(body["items"]) == 2
        _check_namespace(client, body)
        _check_control_post_method("fpoint:add-collection", client, _get_collection_json(), body)
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile_get_method("profile", client, item)
            assert "name" in item
            assert "author" in item

        #test not existing user
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_post(self, client):
        """Tests for CollectionsByUser POST method"""
        valid = _get_collection_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["name"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Test-Collection-1"

        #test with not existing user
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        # test with already exists collection name
        valid["name"] = "Collection1-of-User1"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        #remove field 'name' so document become invalid
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestCollection(object):

    RESOURCE_URL = "/api/users/user-1/collections/Collection1-of-User1/"
    INVALID_URL = "/api/users/user-1/collections/Not-Exist-Collection/"
    INVALID_URL_NOUSER = "/api/users/not-user/collections/Collection1-of-User1/"
    MODIFIED_URL = "/api/users/user-1/collections/Test-Collection-1/"

    def test_get(self, client):
        """Tests for Collection GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "name" in body
        assert "author" in body
        assert len(body["items"]) == 2 #there are already two pre-added recipe
        _check_namespace(client, body)
        _check_profile_get_method("profile", client, body)
        _check_control_get_method("fpoint:collections-by", client, body)
        _check_control_post_method("fpoint:add-recipe", client, _get_recipe_json(), body)
        for item in body["items"]:
            assert "title" in item
            _check_control_get_method("self", client, item)
            _check_profile_get_method("profile", client, item)
        valid = _get_collection_json()
        valid["name"] = body["name"] #avoid changing url
        _check_control_put_method("edit", client, valid, body)
        _check_control_delete_method("fpoint:delete", client, body)

        #test collection not exist
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

        #test user not exist
        resp = client.get(self.INVALID_URL_NOUSER)
        assert resp.status_code == 404

    def test_post(self, client):
        """Tests for Collection POST method"""
        valid = _get_recipe_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == "Extra-Recipe-1"

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #remove field 'ingredients' so document become invalid
        valid.pop("ingredients")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #not-exist collection
        valid = _get_recipe_json(2)
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        #not-exist user
        resp = client.post(self.INVALID_URL_NOUSER, json=valid)
        assert resp.status_code == 404

        #not-exist category or ethnicity
        valid["category"] = "Not-Exist-Category"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        valid = _get_recipe_json(2)
        valid["ethnicity"] = "Not-Exist-Ethnicity"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #valid with rating
        valid = _get_recipe_json(2)
        valid["rating"] = 5.0
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == "Extra-Recipe-2"
        assert body["rating"] == 5.0

    def test_put(self, client):
        """Tests for Collection PUT method"""
        valid = _get_collection_json()

        #test valid but don't change name, add description
        valid["name"] = "Collection1-of-User1"
        valid["description"] = "Test Description"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        #test collection not exist
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        #test user not exist
        resp = client.put(self.INVALID_URL_NOUSER, json=valid)
        assert resp.status_code == 404

        #test wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test missing required field
        valid.pop("name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #test duplicate collection name
        valid["name"] = "Collection2-of-User1"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #test valid with changed URL
        valid = _get_collection_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]

    def test_delete(self, client):
        """Tests for Collection DELETE method"""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        #not exist collection
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
        #not exist user
        resp = client.delete(self.INVALID_URL_NOUSER)
        assert resp.status_code == 404

class TestRecipe(object):

    RESOURCE_URL = "/api/users/user-1/collections/Collection1-of-User1/1/"
    INVALID_URL = "/api/users/user-1/collections/Collection1-of-User1/10/"
    INVALID_URL_NOUSER = "/api/users/no-user/collections/Collection1-of-User1/1/"
    INVALID_URL_NOCOL = "/api/users/user-1/collections/Not-Collection-User1/1/"

    def test_get(self, client):
        """Tests for Recipe GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "title" in body
        assert "ingredients" in body
        assert "description" in body
        assert "ethnicity" in body
        assert "category" in body
        _check_namespace(client, body)
        _check_profile_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_get_method("fpoint:category", client, body)
        _check_control_get_method("fpoint:ethnicity", client, body)
        _check_control_put_method("edit", client, _get_recipe_json(), body)
        _check_control_delete_method("fpoint:delete", client, body)

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
        resp = client.get(self.INVALID_URL_NOUSER)
        assert resp.status_code == 404
        resp = client.get(self.INVALID_URL_NOCOL)
        assert resp.status_code == 404

    def test_put(self, client):
        """Tests for Recipe PUT method"""
        #test valid
        valid = _get_recipe_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        #test recipe not exist
        valid = _get_recipe_json()
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        #test user not exist
        resp = client.put(self.INVALID_URL_NOUSER, json=valid)
        assert resp.status_code == 404

        #test collection ot exist
        resp = client.put(self.INVALID_URL_NOCOL, json=valid)
        assert resp.status_code == 404

        #test invalid content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test invalid document - missing required field
        valid.pop("title")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #test invalid document - wrong type of Rating
        valid = _get_recipe_json()
        valid["rating"] = "4"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #test not-exist category or ethnicity
        valid = _get_recipe_json()
        valid["category"] = "Not-Exist-Category"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        valid = _get_recipe_json(2)
        valid["ethnicity"] = "Not-Exist-Ethnicity"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

    def test_delete(self, client):
        """Tests for Recipe DELETE method"""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        #test recipe not exist
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
        #test user not exist
        resp = client.delete(self.INVALID_URL_NOUSER)
        assert resp.status_code == 404
        #test collection not exist
        resp = client.delete(self.INVALID_URL_NOCOL)
        assert resp.status_code == 404

class TestAllCategories(object):

    RESOURCE_URL = "/api/categories/"

    def test_get(self, client):
        """Tests for AllCategories GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 3 #3 categories are added
        _check_namespace(client, body)
        _check_control_get_method("fpoint:all-users", client, body)
        _check_control_post_method("fpoint:add-category", client, _get_category_json(), body)
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile_get_method("profile", client, item)
            assert "name" in item
            assert "description" in item

    def test_post(self, client):
        """Tests for AllCategories POST method"""
        #test valid
        valid = _get_category_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["name"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Test-Category-1"

        #test wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with already exists category name
        valid["name"] = "category1"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #remove field 'name' so document become invalid
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestCategory(object):

    RESOURCE_URL = "/api/categories/category1/"
    INVALID_URL = "/api/categories/non-exist-category/"
    MODIFIED_URL = "/api/categories/Test-Category-1/"

    def test_get(self, client):
        """Tests for Category GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "category1"
        _check_namespace(client, body)
        _check_profile_get_method("profile", client, body)
        _check_control_get_method("fpoint:all-categories", client, body)
        #test put without changing url
        valid = _get_category_json()
        valid["name"] = "category1"
        _check_control_put_method("edit", client, valid , body)

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """Tests for Category PUT method"""
        #test valid but don't change name
        valid = _get_category_json()
        valid["name"] = "category1"
        valid["description"] = "test description"
        resp = client.put(self.RESOURCE_URL, json=valid)

        #test wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test category not exist
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        #test duplicate name
        valid["name"] = "category2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #test invalid document, missing name
        valid.pop("name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #test valid with changed URL
        valid = _get_category_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]

class TestAllEthnicities(object):

    RESOURCE_URL = "/api/ethnicities/"

    def test_get(self, client):
        """Tests for AllEthnicities GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 3 #3 categories are added
        _check_namespace(client, body)
        _check_control_get_method("fpoint:all-users", client, body)
        _check_control_post_method("fpoint:add-ethnicity", client, _get_ethnicity_json(), body)
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile_get_method("profile", client, item)
            assert "name" in item
            assert "description" in item

    def test_post(self, client):
        """Tests for AllEthnicities POST method"""
        #test valid
        valid = _get_ethnicity_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["name"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Test-Ethnicity-1"

        #test wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with already exists ethnicity name
        valid["name"] = "ethnicity1"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #remove field 'name' so document become invalid
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestEthnicity(object):

    RESOURCE_URL = "/api/ethnicities/ethnicity1/"
    INVALID_URL = "/api/ethnicities/non-exist-ethnicity/"
    MODIFIED_URL = "/api/ethnicities/Test-Ethnicity-1/"

    def test_get(self, client):
        """Tests for Ethnicity GET method"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "ethnicity1"
        _check_namespace(client, body)
        _check_profile_get_method("profile", client, body)
        _check_control_get_method("fpoint:all-ethnicities", client, body)
        #test put without changing url
        valid = _get_ethnicity_json()
        valid["name"] = "ethnicity1"
        _check_control_put_method("edit", client, valid , body)

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """Tests for Ethnicity PUT method"""
        #test valid but don't change name
        valid = _get_ethnicity_json()
        valid["name"] = "ethnicity1"
        valid["description"] = "test description"
        resp = client.put(self.RESOURCE_URL, json=valid)

        #test wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test ethnicity not exist
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        #test duplicate name
        valid["name"] = "ethnicity2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        #test invalid document, missing name
        valid.pop("name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #test valid with changed URL
        valid = _get_ethnicity_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]
