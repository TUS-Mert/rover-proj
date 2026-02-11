import os
import random

from .models import Telemetry
from . import db

try:
    import smbus2
    import bme280

    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False


class SensorManager:
    def __init__(self):
        self.address = 0x76
        self.bus = None
        self.calibration_params = None
        self.simulate = (
            (not HARDWARE_AVAILABLE)
            or (os.getenv("SIMULATE_HARDWARE") == "true")
            or (os.getenv("FLASK_ENV") == "testing")
        )

        if not self.simulate:
            try:
                self.bus = smbus2.SMBus(1)
                self.calibration_params = bme280.load_calibration_params(
                    self.bus, self.address
                )
                print("✅ BME280 Sensor initialized.")
            except Exception as e:
                print(f"❌ BME280 Init Error: {e}")
                print("⚠️ Falling back to Sensor Simulation.")
                self.simulate = True

    def get_readings(self):
        """
        Reads data from the sensor (or generates mock data).
        Returns a dictionary: {'temperature': float, 'humidity': float, 'pressure': float}
        """
        if self.simulate:
            return self._generate_mock_data()

        try:
            data = bme280.sample(self.bus, self.address, self.calibration_params)
            return {
                "temperature": round(data.temperature, 2),
                "humidity": round(data.humidity, 2),
                "pressure": round(data.pressure, 2),
            }
        except Exception as e:
            print(f"⚠️ Sensor Read Failed: {e}")
            return None

    def log_data(self, readings=None):
        """Logs the current sensor readings to the database."""
        if readings is None:
            readings = self.get_readings()

        if not readings:
            return

        # Create a new Telemetry record
        entry = Telemetry(
            temperature=readings.get("temperature"),
            humidity=readings.get("humidity"),
            pressure=readings.get("pressure"),
            timestamp=db.func.now()
        )

        try:
            db.session.add(entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to log telemetry: {e}")

    def _generate_mock_data(self):
        """Generates random data for testing."""

        return {
            "temperature": round(25.0 + random.uniform(-0.5, 0.5), 2),
            "humidity": round(45.0 + random.uniform(-2, 2), 2),
            "pressure": round(1013.0 + random.uniform(-1, 1), 2),
        }


# Create a global instance to be imported by routes
sensor_manager = SensorManager()
