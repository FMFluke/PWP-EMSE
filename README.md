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

Alternatively, you can run command `python populate_db.py <db_file_name>`, replacing `<db_file_name>` with a string you want as name of database file to create a populated database with that filename. If `<db_file_name>` is left out then the default will be `example.db`.

If you have created an empty database manually, you may want to populate it manually as well. In that case, you will need do import `populate_db.py` and utilise its functions there. You will first need to call function `config_database` first to point to the correct database file name .

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
