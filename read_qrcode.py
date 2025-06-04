import cv2
from pyzbar import pyzbar
import csv
import datetime
import os
import sys
import time
from gpiozero import DigitalInputDevice

FLUSH = True
filepath = os.path.dirname(__file__)
log_base_dir = os.path.join(filepath, "logs")
SENSOR_PIN = 9
pir = DigitalInputDevice(SENSOR_PIN)

def load_members(log_path):
    members = {}
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        members[row[0]] = ",".join(row[1:])
        except Exception as e:
            print(f"読み込みエラー: {e}")
    return members

def save_members(log_path, members):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        for name, timestamps in sorted(members.items()):
            times = timestamps.split(',')
            if len(times) > 4:
                times = times[-4:]
            csv_str = name + "," + ",".join(times) + "\n"
            f.write(csv_str)

def run_camera():
    today = datetime.date.today()
    ym_str = today.strftime("%Y-%m")
    ymd_str = today.strftime("%Y-%m-%d")
    log_path = os.path.join(log_base_dir, ym_str, f"{ymd_str}.csv")
    members = load_members(log_path)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)

    str_prv_obj = None
    event_gap = 0

    print("カメラ起動 → QRコードを読み取ってください（最大10秒）")

    try:
        start_time = time.time()
        while time.time() - start_time < 10:
            ret, frame = cap.read()
            if not ret:
                continue

            decoded_objs = pyzbar.decode(frame)
            timestamp = datetime.datetime.now().strftime("%H:%M")

            if event_gap > 0:
                event_gap -= 1

            if event_gap == 0:
                str_prv_obj = None

            for obj in decoded_objs:
                name = obj.data.decode('utf-8', 'ignore')

                if name != str_prv_obj:
                    print(f"{timestamp} ##### {name} さんを検知しました。", file=sys.stderr, flush=FLUSH)
                    str_prv_obj = name

                    if name in members:
                        members[name] += "," + timestamp
                    else:
                        members[name] = timestamp

                    save_members(log_path, members)
                    event_gap = 300
                    print(f"{timestamp} ##### Start event_gap（連続読み取り防止用のクールタイム開始）", file=sys.stderr, flush=FLUSH)

    finally:
        cap.release()
        print("カメラ停止")

def wait_for_sensor():
    print("センサー監視中...（1秒以上反応でカメラ起動）")
    try:
        while True:
            if pir.value == 1:
                start = time.time()
                while pir.value == 1:
                    if time.time() - start >= 1:
                        run_camera()
                        break
                    time.sleep(0.1)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n終了します")

if __name__ == "__main__":
    wait_for_sensor()
