import threading
from flask import (
    Blueprint,
    render_template,
    Response,
    abort,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
)
from flask_jwt_extended import create_access_token
from flask_login import login_required, current_user

from app import db, socketio
from app.models import User, UserPrivilege
from . import streaming
from .sensors import sensor_manager

main_bp = Blueprint("main", __name__)

# Background thread for BME280
thread = None
thread_lock = threading.Lock()


def background_sensor_thread():
    """Sends sensor data to clients every 2 seconds."""
    ticks = 0
    while True:
        socketio.sleep(2)
        data = sensor_manager.get_readings()
        if data:
            socketio.emit("bme_data", data)

            # Log data to DB every minute (30 * 2s = 60s)
            ticks += 1
            if ticks >= 30:
                sensor_manager.log_data(data)
                ticks = 0


@main_bp.route("/")
@login_required
def index():
    """Render the main dashboard page."""
    if not current_user.can_read:
        return render_template("auth/unauthorized.html"), 403

    # Start the background thread if it's not running
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_sensor_thread)

    # Generate token for the logged-in user and pass it to the template
    access_token = create_access_token(identity=current_user.email)
    return render_template("index.html", token=access_token)


@main_bp.route("/video_feed")
@login_required
def video_feed():
    """Video streaming route."""
    if not current_user.can_read:
        abort(403)
    return Response(
        streaming.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@main_bp.route("/api/sensors")
@login_required
def get_sensor_data():
    """API endpoint to fetch current sensor data."""
    data = sensor_manager.get_readings()
    if data:
        return jsonify(data)
    return jsonify({"error": "Sensor read failed"}), 500


# The /token route is no longer needed as it's generated on dashboard load
@main_bp.route("/logs")
@login_required
def logs():
    """Placeholder for a future logs page."""
    return "Logs page coming soon.", 200


@main_bp.route("/grant_privilege")
@login_required
def grant_privilege():
    # 1. Security Check: Only Admins allowed
    if not current_user.is_admin:
        abort(403)

    # 2. Fetch all users (ordered by ID)
    users = User.query.order_by(User.id).all()

    # 3. Render template with data
    return render_template(
        "auth/privilege_granting.html", users=users, UserPrivilege=UserPrivilege
    )


@main_bp.route("/update_user_role/<int:user_id>", methods=["POST"])
@login_required
def update_user_role(user_id):
    # Security Check
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    new_role_name = request.form.get("privilege")

    # Prevent Admin from locking themselves out
    if user.id == current_user.id and new_role_name != "ADMIN":
        flash("You cannot remove your own Admin privileges!", "danger")
        return redirect(url_for("main.grant_privilege"))

    try:
        if new_role_name in UserPrivilege.__members__:
            user.privilege = UserPrivilege[new_role_name]
            db.session.commit()
            flash(f"Updated {user.email} to {new_role_name}", "success")
        else:
            flash("Invalid role selected.", "warning")

    except Exception as e:
        db.session.rollback()
        flash(f"Error updating user: {str(e)}", "danger")

    return redirect(url_for("main.grant_privilege"))
