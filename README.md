# PWP SPRING 2019
# Foodpoint
# Group information
* Student 1. Sirapop Wongstapornpat (wong.sirapop(at)gmail.com)
* Student 2. Muhammad Laiq (ujankhan66(at)gmail.com)
* Student 3. Clement John Shaji (clementjohnshaji(at)gmail.com)
-----
# Database setup (DL2)
## Requirements
This project requires `Flask`, `pysqlite3`, `flask-sqlalchemy`. Using `ipython` as console is also recommended but not required.    
For testing, we also requires `pytest` and `pytest-cov`.    
All dependencies can be installed using `pip install` command followed by the name of library, or alternatively execute this command in terminal to install all libraries needed (recommended because it pinpoints the correct version):     
`pip install -r requirements.txt`    

## Creating and populating the database
The database can be created by running the following two lines of code from python console. (Assuming current directory is same with `database.py`)    
```python
from database import db    
db.create_all()    
```    
Database will be stored in file name `test.db` at the same directory. The created database will be empty.    

Alternatively, you can run command `python populate_db.py <db_file_name>`, replacing `<db_file_name>` with a string you want as name of database file to create a populated database with that filename. If `<db_file_name>` is left out then the default will be `test.db`.

If you have created an empty database manually, you may want to populate it manually as well. In that case, you will need do import `populate_db.py` and utilise its functions there. You will first need to call function `config_database` first to point to the correct database file name.    
An example code of adding a user into empty `test.db` would be:    
```python
import populate_db as handle
from database import User

handle.config_database("test") #point to the right file
try:
    handle.add_user("Frodo Baggins", "fbaggins")
except IntegrityError:
    print("Unsuccessful add, userName not unique.")
```

You can see comments inside `populate_db.py` for the documentation of using its functions to populate database.
# Database Testing (DL2)
## Test Setup
After setting up database now we are ready to test our database,  All Python modules that either begin with `_test` or `test_` are  automatically detected by pytest. Once you have some tests, you can just type pytest into the terminal when in the project directory to run all test.
```python
import os
import pytest
import tempfile

import app

@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    with app.app.app_context():
        app.db.create_all()

    yield app.db

    os.close(db_fd)
    os.unlink(db_fname)
```
## Implementation detail:
Using yield in a fixture enables the same function to handle both setup (before yield) and teardown (after yield). After creating this fixture, your tests can obtain a fresh database by including db_handle in their parameters.
Another thing is to enable foreign key support (like we did in the app itself), and to import all models from the app. Adding these lines after import app does the trick:
```python
import database
from database import User, Recipe, Collection, Category, Ethnicity
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```
After this setup we can do any number of functions whose name starts with test_ and that have `db_handle` as their sole parameter, e.g. `test_create_instances`.
## Writing Test Functions for Models
A test function represents a test case. It typically consists of preparations and one or more assert statements that are used to determine whether the test subject performed correctly. Assert is a Python statement that functions like an if statement, but instead executing a code block if its condition is (equivalent to) True, assert raises `AssertionError` if the condition is (equivalent to) False. The pytest framework has its own traceback analysis for AssertionError (see pytest documentation on assert for examples, https://docs.pytest.org/en/latest/assert.html). You can also write a custom message that will replace the traceback.
When testing models a typical pattern is to create one or more model instances, (try to) save them to the database, and then do assertions about the values stored in the database.
A simple example related to our foodpoint api would be to create a user with some values, and check that it was stored.
We will use create helper functions to avoid extra code.
```python
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
```
Now we will create test case to test our api.
```python
def test_create_user(db_handle):
    """
    Tests that user is present is user model.
    """
    user = _get_user()
    db_handle.session.add(user)
    db_handle.session.commit()
    assert User.query.count() == 1
```
This test will fail if either there is an error in committing the transaction, or if for some reasons there isn't exactly 1 user in the database (remember that each test case is run on a fresh empty database).
In similiar way you can create further test cases.
#Testing setup guideline text has been taken from excercise #1.
