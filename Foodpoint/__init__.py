import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask import redirect
db = SQLAlchemy()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder="static")
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        #SQLALCHEMY_DATABASE_URI = "sqlite:///test.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    #This function is brought from example in the exercise
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from . import database
    app.cli.add_command(database.init_db_command)

    from . import populate_db
    app.cli.add_command(populate_db.populate_database_example)

    from . import api
    app.register_blueprint(api.api_bp)

    from Foodpoint.utils import LINK_RELATIONS_URL
    from Foodpoint.utils import APIARY_URL

    @app.route(LINK_RELATIONS_URL)
    def namespace():
        return redirect(APIARY_URL + "link-relations")

    @app.route("/profiles/<resource>/")
    def profile(resource):
        return redirect(APIARY_URL + resource)

    @app.route("/recipebook/")
    def client():
        return app.send_static_file("html/recipebook.html")

    return app
