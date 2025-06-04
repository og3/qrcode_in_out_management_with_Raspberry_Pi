import cv2
from pyzbar import pyzbar
import csv
import datetime
import os
import sys

FLUSH = True
filepath = os.path.dirname(__file__)
log_base_dir = os.path.join(filepath, "logs")

# デフォルトのメンバー
members = {
    "01ChibaHanako": "",
    "02SaitamaHiroshi": "",
    "03TokyoTaro": "",
    "04YokohamaYoko": "",
}

# 日付情報
today = datetime.date.today()
ym_str = today.strftime("%Y-%m")
ymd_str = today.strftime("%Y-%m-%d")
log_dir = os.path.join(log_base_dir, ym_str)
log_path = os.path.join(log_dir, f"{ymd_str}.csv")

# CSV読み込み（存在すれば）
if os.path.exists(log_path):
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            mlist = list(reader)
            members = {m[0]: m[1] for m in mlist if len(m) > 1}
    except Exception as e:
        print(f"読み込みエラー: {e}")
else:
    print(f"{log_path} not found")

# カメラ初期化
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 15)

str_prv_obj = None
event_gap = 0

print("QRコードをカメラで読み取ってください（Ctrl+Cで終了）")

try:
    while True:
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

                    # ログディレクトリ作成
                    os.makedirs(log_dir, exist_ok=True)

                    # CSV出力
                    with open(log_path, "w", encoding="utf-8") as f:
                        for s in sorted(members.items()):
                            times = s[1].split(',')
                            if len(times) > 4:
                                times = times[-4:]
                            csv_str = s[0] + "," + ",".join(times) + "\n"
                            f.write(csv_str)

                    event_gap = 300
                    print(f"{timestamp} ##### Start event_gap", file=sys.stderr, flush=FLUSH)
                else:
                    print(f"{timestamp} ##### Unknown QR: {str_dec_obj}", file=sys.stderr, flush=FLUSH)

except KeyboardInterrupt:
    print("\n終了します")
finally:
    cap.release()
