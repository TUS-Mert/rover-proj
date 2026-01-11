from flask import Blueprint, render_template, jsonify
from app.models import Telemetry # We'll use this to pull real data

# Create a Blueprint named 'main'
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/telemetry')
def get_telemetry():
    # Pull the most recent entry from Postgres
    latest = Telemetry.query.order_by(Telemetry.timestamp.desc()).first()
    
    if latest:
        return jsonify({
            "cpu_temp": round(latest.cpu_temp, 1),
            "battery": int(latest.battery_level * 100)
        })
    
    return jsonify({"cpu_temp": "N/A", "battery": "N/A"}), 404