# PWP SPRING 2019
# Foodpoint
# Group information
* Student 1. Sirapop Wongstapornpat (wong.sirapop(at)gmail.com)
* Student 2. Muhammad Laiq (ujankhan66(at)gmail.com)
* Student 3. Clement John Shaji (clementjohnshaji(at)gmail.com)
-----
# Database setup (DL2)
## Requirements
This project requires `Flask`, `pysqlite3`, `flask-sqlalchemy`.    
Using `ipython` as console is also recommended but not requires.    
For testing, we also requires `pytest` and `pytest-cov`    
All dependencies can be installed using `pip install` command followed by the name of library, or alternatively execute this command:     
`pip install -r requirements.txt`    

## Creating the database
The database can be created by running the following two lines of code from python console. (Assuming current directory is same with `database.py`)    
    from database import db    
    db.create_all()    
Database will be stored in file name `test.db` at the same directory. The file's name can be changed by editing the line `app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"` in the `database.py`    
