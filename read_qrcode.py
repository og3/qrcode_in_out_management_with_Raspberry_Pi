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

# センサー設定（GPIO9 = BCMモードで9番ピン）
SENSOR_PIN = 9
pir = DigitalInputDevice(SENSOR_PIN)

def load_members(log_path):
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                mlist = list(reader)
                return {m[0]: m[1] for m in mlist if len(m) > 1}
        except Exception as e:
            print(f"読み込みエラー: {e}")
    else:
        print(f"{log_path} not found")
    # 初期メンバー
    return {
        "01ChibaHanako": "",
        "02SaitamaHiroshi": "",
        "03TokyoTaro": "",
        "04YokohamaYoko": "",
    }

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
    log_dir = os.path.join(log_base_dir, ym_str)
    log_path = os.path.join(log_dir, f"{ymd_str}.csv")
    members = load_members(log_path)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)

    str_prv_obj = None
    event_gap = 0

    print("カメラ起動 → QRコードを読み取ってください（Ctrl+Cで中断）")

    try:
        start_time = time.time()
        while time.time() - start_time < 10:  # 10秒間だけカメラを起動
            ret, frame = cap.read()
            if not ret:
                continue

            decoded_objs = pyzbar.decode(frame)
            timestamp = datetime.datetime.now().strftime("%H:%M")

            if event_gap > 0:
                event_gap -= 1

            if event_gap == 0 and str_prv_obj is not None:
                str_prv_obj = None
                print(f"{timestamp} ##### Event trigger reset", file=sys.stderr, flush=FLUSH)

            for obj in decoded_objs:
                str_dec_obj = obj.data.decode('utf-8', 'ignore')

                if str_dec_obj != str_prv_obj:
                    name = str_dec_obj
                    if name in members:
                        print(f"{timestamp} ##### Detected: {str_dec_obj}", file=sys.stderr, flush=FLUSH)
                        str_prv_obj = str_dec_obj
                        if members[name] == "":
                            members[name] = timestamp
                        else:
                            members[name] += "," + timestamp
                        save_members(log_path, members)
                        event_gap = 300
                        print(f"{timestamp} ##### Start event_gap", file=sys.stderr, flush=FLUSH)
                    else:
                        print(f"{timestamp} ##### Unknown QR: {str_dec_obj}", file=sys.stderr, flush=FLUSH)

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
