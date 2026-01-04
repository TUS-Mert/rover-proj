import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the db object here so it can be imported by models
db = SQLAlchemy()

def create_app():
    load_dotenv()  # Load environment variables from .env file
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://mert:password@localhost/roverdb')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Bind db to this app
    db.init_app(app)

    # CRITICAL: Import the models folder here
    # This triggers app/models/__init__.py which loads all your tables
    with app.app_context():
        from . import models 

    return app