import time
from gpiozero import DigitalInputDevice
from config import SENSOR_PIN

class SensorWatcher:
    def __init__(self):
        self.sensor = DigitalInputDevice(SENSOR_PIN)

    def wait_for_trigger(self, duration=1.0):
        if self.sensor.value == 1:
            start = time.time()
            while self.sensor.value == 1:
                if time.time() - start >= duration:
                    return True
                time.sleep(0.1)
        return False
