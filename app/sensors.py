from abc import ABC, abstractmethod
import os
import random
from dataclasses import dataclass, field
from collections import defaultdict
from webbrowser import get

from .models import Telemetry
from . import db

try:
    import smbus2
    import bme280

    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False


@dataclass
class Sensor(ABC):
    address: int = field(default_factory=int)
    bus = None
    calibration_params = None

    @abstractmethod
    def get_readings(self) -> dict:
        pass
    
    

@dataclass
class BME280Sensor(Sensor):

    def __post_init__(self):
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
            json_data = {
                "temperature": round(data.temperature, 2),
                "humidity": round(data.humidity, 2),
                "pressure": round(data.pressure, 2),
            } 


            return json_data 
        except Exception as e:
            print(f"⚠️ Sensor Read Failed: {e}")
            return {}


    def _generate_mock_data(self):
        """Generates random data for testing."""

        return {}


@dataclass
class SensorManager:
    sensors: list = field(default_factory=list)

    def get_average_readings(self):
        data = defaultdict(list)
        for sensor in self.sensors:
            readings = sensor.get_readings()
            
            for key in readings.keys():
                data[key].append(readings[key])
        
        avg_data = {}
        for key in data.keys():
            avg_data[key] = round(sum(data[key]) / len(data[key]), 2)
        
        return avg_data
            
    def log_data(self, data: dict = {}):

        if not data:
            data = self.get_average_readings()
        
        entry = Telemetry(
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            pressure=data.get("pressure"),
            timestamp=db.func.now()
        )

        try:
            db.session.add(entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to log telemetry: {e}")
    


sensor_x76 = BME280Sensor(address=0x76)
sensor_x77 = BME280Sensor(address=0x77)


# Create a global instance to be imported by routes
sensor_manager = SensorManager(sensors=[sensor_x76, sensor_x77])
