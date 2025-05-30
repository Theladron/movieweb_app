import os

from dotenv import load_dotenv
from flask import Flask

from db_validator import validate_database
from extensions import db
from managers import data_manager
from routes import register_blueprints

load_dotenv()


def create_app():
    """
    Creates and configures the Flask application, calls for
    database validation and blueprint registration.
    """
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    data_folder = os.path.join(basedir, 'data')
    db_file = os.path.join(data_folder, 'movies.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"

    db.init_app(app)
    data_manager.init_app(app)  # initialize with app here

    validate_database(app)
    register_blueprints(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
