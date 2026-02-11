from .. import db
from datetime import datetime, timezone


class Telemetry(db.Model):
    __tablename__ = "telemetry"

    id = db.Column(db.Integer, primary_key=True)
    # Use index=True for the timestamp because you'll query by time often
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))

    cpu_temp = db.Column(db.Float)
    battery_level = db.Column(db.Float)  # Percentage 0.0 - 1.0
    wifi_strength = db.Column(db.Integer)  # dBm
    humidity = db.Column(db.Float)  # Percentage 0.0 - 100.0
    temperature = db.Column(db.Float)  # Celsius
    pressure = db.Column(db.Float)  # hPa

    # Optional: track which "session" this belongs to
    session_id = db.Column(db.String(50), nullable=True)
