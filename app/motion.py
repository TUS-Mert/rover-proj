import os
from gpiozero import Robot, Servo

# Check if we are on the RPi or Laptop
if os.getenv('ENV') == 'production':
    from gpiozero.pins.lgpio import LPiFactory
    factory = LPiFactory()
else:
    # On WSL, this allows the code to run without hardware
    from gpiozero.pins.mock import MockFactory
    factory = MockFactory()
    print("Running with Mock Hardware")

class MotionController:
    def __init__(self):
        # Pins from your Software Architecture Specification [cite: 107]
        self.rover = Robot(left=(17, 18), right=(22, 23), pin_factory=factory)
        self.camera = Servo(25, pin_factory=factory)