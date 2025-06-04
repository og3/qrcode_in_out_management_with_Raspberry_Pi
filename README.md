# アプリケーション概要
- (1) 入場・退場するときにQRコードをRaspberryPiのカメラにかざします。QRコードには各メンバーの「名前」が記録されています。
- (2) 入退場記録アプリケーションはQRコードを読み取った時間をQRコードから読み取った「名前」を識別子とするレコードに記録してファイルに書き込みます。ファイルはCSV形式です。

## GPIO9番に赤外線センサーを接続してカメラのオンオフを制御する
![IMG_20250604_150018](https://github.com/user-attachments/assets/d2654ca5-d8be-4b17-8963-4492818ecfe1)

## 実行イメージ
```bash
カメラ起動 → QRコードを読み取ってください（最大10秒）
14:42 ##### Detected: 02SaitamaHiroshi
14:42 ##### Start event_gap
14:42 ##### Detected: 01ChibaHanako
14:42 ##### Start event_gap
カメラ停止
カメラ起動 → QRコードを読み取ってください（最大10秒）
カメラ停止
```
## QRコードの作成
```bash
$ sudo apt install python3-qrcode
$ qr "Hello" > qr_hello.png
```
