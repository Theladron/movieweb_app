import os
from flask import Flask
from db_validator import validate_database
from routes import register_blueprints
from extensions import db
from managers import data_manager

def create_app():
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
