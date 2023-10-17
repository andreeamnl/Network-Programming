# app.py
from flask import Flask
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger




from models.database import db
from models.electro_scooter import ElectroScooter





def create_app():
    app = Flask(__name__)
    # Configure SQLAlchemy to use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    db.init_app(app)
    Swagger(app)

    return app
if __name__ == "__main__":
    
    app = create_app()
    import routes
    app.run()
