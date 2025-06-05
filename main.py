import time
import datetime
from qr import QRCodeReader
from sensor import SensorWatcher
from buzzer import Notifier
from logger import LogManager
from config import EVENT_GAP_FRAMES, CAMERA_RUNTIME


def main():
    print("センサー監視中...（1秒以上反応でカメラ起動）")
    sensor = SensorWatcher()
    notifier = Notifier()
    logger = LogManager()
    str_prv_obj = None
    event_gap = 0

    try:
        while True:
            if sensor.wait_for_trigger():
                qr_reader = QRCodeReader()
                print("カメラ起動 → QRコードを読み取ってください")
                start_time = time.time()

                while time.time() - start_time < CAMERA_RUNTIME:
                    if event_gap > 0:
                        event_gap -= 1
                    if event_gap == 0:
                        str_prv_obj = None

                    names = qr_reader.read_frame()
                    timestamp = datetime.datetime.now().strftime("%H:%M")

                    for name in names:
                        if name != str_prv_obj:
                            print(f"{timestamp} ##### {name} さんを検知しました。")
                            notifier.beep()
                            logger.update(name, timestamp)
                            str_prv_obj = name
                            event_gap = EVENT_GAP_FRAMES
                qr_reader.release()
                print("カメラ停止")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n終了します")


if __name__ == "__main__":
    main()
