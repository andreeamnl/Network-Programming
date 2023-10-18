# app.py
from flask import Flask
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger
import json



from models.database import db
from models.electro_scooter import ElectroScooter



with open("config.json",'r') as config_file:
    config = json.load(config_file)


def create_app():
    app = Flask(__name__)
    # Configure SQLAlchemy to use postgresql
    app.config['SQLALCHEMY_DATABASE_URI'] = config["database_url"]
    db.init_app(app)
    Swagger(app)

    return app
if __name__ == "__main__":
    
    app = create_app()
    import routes
    app.run()
