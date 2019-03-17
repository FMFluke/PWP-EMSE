from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#This function is brought from example in the exercise
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

"""
Table RecipeCollection
----------------------
This table contains mapping of recipe and collection that it belongs in.
Columns:
- collectionId, INTEGER, PRIMARY KEY, contains id of collection with Foriegn key relation to Collection table
- recipeId, INTEGER, PRIMARY KEY, contains id of recipe with Foriegn key relation to Recipe table
"""
RecipeCollection = db.Table("RecipeCollection",
    db.Column("collectionId", db.Integer, db.ForeignKey("collection.id", ondelete="CASCADE"), primary_key=True),
    db.Column("recipeId", db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
)

"""
Table User
----------------------
This table contains data about each user.
Columns:
- id, INTEGER, PRIMARY KEY, contains id of each user.
- name, STRING, Max Length 30, NOT NULL, contains name of the user.
- userName, STRING, Max Length 20, NOT NULL, UNIQUE, contains unique string identifier of the user.
"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    userName = db.Column(db.String(20), nullable=False, unique=True)

    collections = db.relationship("Collection", cascade="all,delete", back_populates="user")

"""
Table Recipe
----------------------
This table contains data about each recipe.
Columns:
- id, INTEGER, PRIMARY KEY, contains id of each recipe.
- title, STRING, Max Length 30, NOT NULL, contains title or name of the recipe.
- description, STRING, Max Length 200, NOT NULL, contains text description of the recipe.
- ingredients, STRING, Max Length 200, NOT NULL, contains ingredients of the recipe in text.
- rating, FLOAT, Range 0-5, contains rating of the recipe.
- ethnicityId, INTEGER, NOT NULL, id of ethnicity of this recipe with Foriegn key relation to Ethnicity table.
- categoryId, INTEGER, NOT NULL, id of category of this recipe with Foriegn key relation to Category table.
"""
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ethnicityId = db.Column(db.Integer, db.ForeignKey("ethnicity.id"), nullable=False)
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    collections = db.relationship("Collection", secondary=RecipeCollection, back_populates="recipes")
    ethnicity = db.relationship("Ethnicity", back_populates="recipes")
    category = db.relationship("Category", back_populates="recipes")

"""
Table Collection
----------------------
This table contains data about each collection.
Columns:
- id, INTEGER, PRIMARY KEY, contains id of each collection.
- name, STRING, Max Length 40, NOT NULL, contains title or name of the collection.
- userId, INTEGER, NOT NULL, id of user that create this collection.
"""
class Collection(db.Model):
    __table_args__ = (db.UniqueConstraint("name", "userId", name="_user_title_uc"), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(100))
    userId = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    recipes = db.relationship("Recipe", secondary=RecipeCollection, back_populates="collections")
    user = db.relationship("User", back_populates="collections")

"""
Table Category
----------------------
This table contains categories available in the system.
Columns:
- id, INTEGER, PRIMARY KEY, contains id of each category.
- name, STRING, Max Length 40, NOT NULL, contains title or name of the category.
"""
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    description = db.Column(db.String(100))

    recipes = db.relationship("Recipe", back_populates="category")

"""
Table Ethnicity
----------------------
This table contains categories available in the system.
Columns:
- id, INTEGER, PRIMARY KEY, contains id of each ethnicity.
- name, STRING, Max Length 40, NOT NULL, contains title or name of the ethnicity.
"""
class Ethnicity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    description = db.Column(db.String(100))

    recipes = db.relationship("Recipe", back_populates="ethnicity")
