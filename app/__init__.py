import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

# Initialize the db object here so it can be imported by models
db = SQLAlchemy()
socketio = SocketIO(manage_session=False)

def create_app():
    load_dotenv()
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-dev-secret')

    # Bind extensions to this app
    db.init_app(app)
    JWTManager(app)
    socketio.init_app(app, cors_allowed_origins="*")

    with app.app_context():
        from . import models 
    
    # Import and register blueprints and socket events
    from . import routes
    from . import websocket
    app.register_blueprint(routes.main_bp)

    return app