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
from app.models import CommandLog, User, UserPrivilege
from . import streaming

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """Render the main dashboard page."""
    if not current_user.can_read:
        return render_template("auth/unauthorized.html"), 403

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

# The /token route is no longer needed as it's generated on dashboard load
@main_bp.route("/logs")
@login_required
def logs():
    """Displays the last 20 system logs."""
    if not current_user.can_read:
        return render_template("auth/unauthorized.html"), 403

    logs = CommandLog.query.order_by(CommandLog.created_at.desc()).limit(20).all()
    return render_template("logs/logs.html", logs=logs)


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
