#from time import sleep
import tkinter as tk
 
import cv2
from PIL import Image, ImageTk
from pyzbar import pyzbar
 
import csv
import datetime
import os, sys
 
# TkinterをVSCodeリモート実行する場合の DISPLAY定期
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')
# ファイルの絶対パス
filepath = os.path.dirname(__file__) 
 
# Log print flush True/False
FLUSH = True
 
class Qreader(tk.Frame):
    def __init__(self, master=None, members=None):
        super().__init__(master)
        self.pack()
        self.members = members
        self.create_widgets()
 
    def create_widgets(self):
        # 画面サイズ 横:640 縦:480
        self.CANVAS_X = 640
        self.CANVAS_Y = 480
        # カメラ画像表示用 tkinter キャンバス定義
        self.canvas = tk.Canvas(self, width=self.CANVAS_X, height=self.CANVAS_Y)
        self.canvas.pack()
        # OpenCVビデオキャプチャ定義
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.CANVAS_X)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CANVAS_Y)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.image_tk = None
        self.str_prv_obj = None
        self.event_gap = 0
        self.capture_code()
 
    def capture_code(self):
        tm_now = datetime.datetime.now()
        timestamp = tm_now.strftime("%H:%M")
        if self.event_gap != 0:
            self.event_gap -= 1
        # QR 検出後１分経過したので最後の検出者名をクリア
        if self.event_gap == 0 and self.str_prv_obj is not None:
            self.str_prv_obj = None
            print(timestamp, '##### Event trigger on!', file=sys.stderr, flush=FLUSH)
 
        ret, frame = self.cap.read()
        if ret == False:
            print(timestamp, "##### Not Image", file=sys.stderr, flush=FLUSH)
        else:
            self.canvas.delete('all')
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            self.image_tk = ImageTk.PhotoImage(image_pil)
            self.canvas.create_image(self.CANVAS_X / 2, self.CANVAS_Y / 2, image=self.image_tk)
            # QRコード読み込み
            decoded_objs = pyzbar.decode(frame)
            if decoded_objs != []:
                # QRコードを検出した場合の処理
                for obj in decoded_objs:
                    #print('Type: ', obj)
 
                    str_dec_obj = obj.data.decode('utf-8', 'ignore')
                    #print('QR code: {}'.format(str_dec_obj))
                    left, top, width, height = obj.rect
 
                    self.canvas.create_rectangle(left, top,
                                            left + width, top + height,
                                            outline='green', width=5)
 
                    self.canvas.create_text(left + (width / 2), top - 30, text=str_dec_obj,
                                       font=('Helvetica', 20, 'bold'), fill='firebrick1')
 
                if str_dec_obj != self.str_prv_obj:
                    name = str_dec_obj
                    if name in self.members:
                        print(timestamp,"##### Detected: ",str_dec_obj, file=sys.stderr, flush=FLUSH)
                        self.str_prv_obj = str_dec_obj
                        if self.members[name] == "":
                            self.members[name] = timestamp
                        else:
                            self.members[name] = self.members[name] + "," + timestamp
 
                        csvlist = [s for s in self.members.items()]
 
                        # csvで入退出時間を記録
                        with open(filepath + "/today.csv", "w", encoding="utf-8") as f:
                            for s in sorted(csvlist):
                                # タイムスタンプが５個以上の場合後ろから４個が有効
                                if len(s[1].split(',')) > 4:
                                    tm = s[1].split(',')
                                    csv_str = s[0]+","+tm[-4]+","+tm[-3]+","+tm[-2]+","+tm[-1]+"\n"
                                else:
                                    csv_str = s[0]+","+s[1]+"\n"
                                f.write(csv_str)
 
                        #self.event_gap = 170
                        self.event_gap = 300
                        print(timestamp, '##### Start event_gap', file=sys.stderr, flush=FLUSH)
 
                    else:
                        print(timestamp,"##### There is no name:",str_dec_obj, file=sys.stderr, flush=FLUSH)
 
        self.after(20, self.capture_code)
 
if __name__ == "__main__":
    # デフォルトmembers辞書
    members = {
    "01ChibaHanako":"",
    "02SaitamaHiroshi":"",
    "03TokyoTaro":"",
    "04YokohamaYoko":"",
    }
 
    root = tk.Tk()
    root.title('QR in-out reader')
    root.geometry('640x480+50+50')
 
    # today.csvを読み込み、名前をkey 入退室時間をvalue で辞書membersを作成
    try:
        with open(filepath + '/today.csv', "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            mlist = list(reader)
            # 
            members = {}
            for m in mlist:
                members[m[0]] = m[1:][0]
 
    except FileNotFoundError:
        # today.csvが存在しないのでディフォルトのmembers辞書を使用する
        print("today.csv not found") 
 
    app = Qreader(master=root, members=members)
    app.mainloop()
 