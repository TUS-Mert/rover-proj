import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# 1. Define extensions FIRST (Global Scope)
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
    login_manager.login_view = 'auth.login'

    # 2. Import models INSIDE the function
    # This breaks the circular dependency because 'db' is already defined above
    with app.app_context():
        from . import models

    # Import and register blueprints
    # Note: Rename imports to avoid shadowing if necessary, but this is fine
    from . import routes
    from . import websocket as websocket
    from . import streaming as streaming
    from .auth import auth_bp
    
    app.register_blueprint(routes.main_bp)
    app.register_blueprint(auth_bp)

    @login_manager.user_loader
    def load_user(user_id):
        # We need to make sure we access the User model correctly
        # Since we imported 'models' inside this function, it is available here
        return models.User.query.get(int(user_id))

    return app