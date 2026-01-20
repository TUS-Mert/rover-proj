import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from . import models  # Import models to register them with SQLAlchemy

# Initialize the db object here so it can be imported by models
db = SQLAlchemy()
socketio = SocketIO(manage_session=False)
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-dev-secret')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-default-session-secret-key')

    # Bind extensions to this app
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Redirect to login page

    # Import and register blueprints and socket events
    from . import routes as routes 
    from . import websocket as websocket
    from . import streaming as streaming # Initialize camera and streaming components
    from .auth import auth_bp
    app.register_blueprint(routes.main_bp)
    app.register_blueprint(auth_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    return app