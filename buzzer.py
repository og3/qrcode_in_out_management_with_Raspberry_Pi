import time
from gpiozero import TonalBuzzer
from config import BUZZER_PIN

class Notifier:
    def __init__(self):
        self.buzzer = TonalBuzzer(BUZZER_PIN)

    def beep(self, freq=440, duration=0.1):
        self.buzzer.play(freq)
        time.sleep(duration)
        self.buzzer.stop()
