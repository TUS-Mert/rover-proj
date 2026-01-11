from flask import Blueprint, render_template, jsonify
from flask_jwt_extended import create_access_token

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@main_bp.route('/token')
def get_token():
    """Generate a JWT for the client."""
    # In a real app, you'd protect this and link it to a user session
    access_token = create_access_token(identity='rover_ui')
    return jsonify(access_token=access_token)

@main_bp.route('/logs')
def logs():
    """Placeholder for a future logs page."""
    return "Logs page coming soon.", 200