from flask import Blueprint, render_template, Response
from flask_jwt_extended import create_access_token
from flask_login import login_required, current_user
from . import streaming

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Render the main dashboard page."""
    # Generate token for the logged-in user and pass it to the template
    access_token = create_access_token(identity=current_user.email)
    return render_template('index.html', token=access_token)

@main_bp.route('/video_feed')
@login_required
def video_feed():
    """Video streaming route."""
    return Response(streaming.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# The /token route is no longer needed as it's generated on dashboard load
@main_bp.route('/logs')
@login_required
def logs():
    """Placeholder for a future logs page."""
    return "Logs page coming soon.", 200