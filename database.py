from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

RecipeCollection = db.Table("RecipeCollection",
    db.Column("collectionId", db.Integer, db.ForeignKey("collection.id"), primary_key=True),
    db.Column("recipeId", db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    userName = db.Column(db.String(20), nullable=False, unique=True)

    collections = db.relationship("Collection", back_populates="user")

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ethnicityId = db.Column(db.Integer, db.ForeignKey("ethnicity.id"), nullable=False)
    categoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    collection = db.relationship("Collection", back_populates="recipes")
    ethnicity = db.relationship("Ethnicity", back_populates="recipes")
    category = db.relationship("Category", back_populates="recipes")

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    recipes = db.relationship("Recipe", back_populates="collection")
    user = db.relationship("User", back_populates="collections")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)

    recipes = db.relationship("Recipe", back_populates="category")

class Ethnicity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)

    recipes = db.relationship("Recipe", back_populates="ethnicity")
