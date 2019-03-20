import os
import pytest
import tempfile
import json

from Foodpoint import create_app, db
from Foodpoint.database import User, Recipe, Collection, Category, Ethnicity
from sqlalchemy.exc import IntegrityError, StatementError

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
        _populate_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    """
    Pre-populate database with 3 users each with one collection which contains one recipe.
    """
    with app.app_context():
        for i in range(1,3):
            user = User(name="User Name{}".format(i),
                        userName="user-{}".format(i)
                    )
            collection = Collection(name="Collection-of-User{}".format(i))
            collection.user = user
            category = Category(name="category{}".format(i))
            ethnicity = Ethnicity(name="ethnicity{}".format(i))
            recipe = Recipe(title="test-recipe{}".format(i),
                            description="description",
                            ingredients="ingredients"
                        )
            recipe.category = category
            recipe.ethnicity = ethnicity
            collection.recipes.append(recipe)
            db.session.add(user)
            db.session.add(ethnicity)
            db.session.add(category)
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
    assert resp.status_code == 200

def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.

    This function is adapted from example in exercise 3 testing part.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

def _check_control_post_method(ctrl, client, obj):
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
    body = _get_sensor_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

def _get_user_json(number=1):
    """
    Generate valid json document for PUT and POST test of user resource
    """
    return {"name": "Extra Testname{}".format(number), "userName": "extratestname{}".format(number)}

class TestAllUsers(object):
    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 3
        _check_namespace(client, body)
        _check_control_post_method("fpoint:add-user", client, body)
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item
            assert "userName" in item

    def test_post(self, client):
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
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "User Name1"
        assert body["userName"] == "user-1"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("fpoint:all-users", client, body)
        _check_control_get_method("fpoint:collections-by", client, body)
        #check put
        #check delete

        #not exist
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
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
        valid = _get_sensor_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404