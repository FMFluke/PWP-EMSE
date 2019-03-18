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
The database can be created by running the command `flask init-db` from the directory above the Foodpoint folder. Note that you need to export the `FLASK_APP` environment to Foodpoint folder before using this command. For example use `export FLASK_APP=Foodpoint`    
Database will be created according to the configuration of the app which could be passed to function `create_app` in `__init__.py` inside Foodpoint folder by having a file `config.py`. Otherwise it will default to `development.db` hardcoded in the function. The created database will be empty.    

To populate database with initial example values, run the command `flask populate_db`

If you want to populate it manually, you will need to import `populate_db.py` and utilise its functions there. These functions will point to the database file as configured in `creat_app` function automatically.

An example code of adding a user into empty `test.db` would be:    
```python
import populate_db as handle
from database import User

try:
    handle.add_user("Frodo Baggins", "fbaggins")
except IntegrityError:
    print("Unsuccessful add, userName not unique.")
```

You can see comments inside `populate_db.py` for the documentation of using its functions to populate database.
## Testing Database
After setting up database now we are ready to test database, put `test_database.py` under same directory of as `database.py`.
Test cases can be executed by typing `pytest` command (assuming that you are at test_database directory), `pytest`  will automatically detect python modules that either begin with `_test` or `test_` .
After executing that command you can check all details in command window about test cases i.e. passed or failed .

An example code of adding new test case into test_database.py would be:
```python
def test_create_user(db_handle):
    """
    Tests that user is added properly in user model.
    """
    user = _get_user()
    db_handle.session.add(user)
    db_handle.session.commit()
    assert User.query.count() == 1
```
