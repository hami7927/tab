import os                     # path.exists使うため
import time                   # sleep 使うため
from ctypes import windll     # sleep の精度を高めるため
import cv2                    # 画像処理
import numpy as np            # 画像処理
import win32gui               # They Are Billionsの画像抽出、描画用画面
import win32ui                # They Are Billionsの画像抽出
import playsound              # 音を鳴らす
import configparser           # Iniファイル読み込み
import threading              # スレッド
import wx                     # 描画用画面
import atexit                 # 描画用画面
import win32con               # 描画用画面
import win32api               # 描画用画面


alert = 'alert.mp3'             # アラート音のファイル名（デフォルト）
name = 'They Are Billions'      # ゼイビリのウィンドウ名（デフォルト）

# プログラム状態
# 0:They Are Billions の画面作成待ち状態
# 1:初日開始待ちで監視前状態
# 2:監視状態
status = 0

# ミニマップの画面上での座標
mmap_top    = 0
mmap_bottom = 0
mmap_left   = 0
mmap_right  = 0

# 日付の画面上での座標
date_top    = 0
date_bottom = 0
date_left   = 0
date_right  = 0

frame = None     # 描画用画面

alert_info = np.array([[0, 1, 0, 0, 0, 0, 0]])     # アラート情報 : 番号、フラグ、座標の上、下、左、右、時間
alert_num = 0                                      # アラート番号
alert_invalidate_sec = 4                           # アラート無効化秒数（数字の根拠なし）
alert_invalidate_range = 0                         # アラート無効化範囲（ドット数）

base_wait_time = 0.016        # アラート確認の周期（秒）


# 描画用画面クラス
class AppFrame( wx.Frame )  :
    def __init__( self )  :
        global mmap_top,mmap_bottom,mmap_left,mmap_right
        self.draw_num = 0

        # 常に最前面、境界線なし
        wx.Frame.__init__( self, None, -1,
                           style = wx.STAY_ON_TOP | wx.BORDER_NONE,
                           pos   = (mmap_left,mmap_top),
                           size  = (mmap_right - mmap_left, mmap_bottom - mmap_top)
                           )

        hwnd = self.GetHandle()
        # 拡張ウィンドウスタイルを取得
        exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        # ウィンドウスタイルに透過、入力受付不可、アクティブ化不可を追加
        win32gui.SetWindowLong( hwnd, win32con.GWL_EXSTYLE,
                                exStyle | win32con.WS_EX_LAYERED | win32con.WS_DISABLED | win32con.WS_EX_NOACTIVATE )
        # 黒を透過色に設定
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 0, win32con.LWA_COLORKEY)
        self.Bind(wx.EVT_PAINT,self.OnPaint)

        # 33ミリ秒ごとに画面リフレッシュして描画するタイマーセット（間隔に根拠なし）
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(33)

    def OnPaint(self, evt):
        # BufferedDCを作らないと透明ウィンドウにならない
        dc = wx.PaintDC(self)
        dc = wx.BufferedDC(dc)
        dc.SetBackground(wx.BLACK_BRUSH)
        dc.Clear()
        dc.SetBrush(wx.BLACK_BRUSH)

        # アラートを描画
        for alt in alert_info:
            if alt[0] != 0 and alt[1] == 1:
                dc.SetPen(wx.YELLOW_PEN)
                dc.DrawCircle(int((alt[4]+alt[5])/2), int((alt[2]+alt[3])/2), 10 - self.draw_num*2)
        self.draw_num = (self.draw_num + 1) % 3

    def onTimer(self,event):
        self.Refresh(False)


# 画像が同じものか判断する
def IsMatch(img, template):
    if template is None or img is None:
        return False

    method = cv2.TM_CCOEFF_NORMED  
    res = cv2.matchTemplate(img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # 画像が同じかの閾値。閾値は実験して決めた
    if max_val < 0.95:
        return False
    return True


# アラートを鳴らす
def PlayAlert():
    global alert
    playsound.playsound(alert)


# 描画用画面を作成
def OpenAppWindow():
    global frame

    app = wx.App( False )
    frame = AppFrame()
    frame.Show()
    app.MainLoop()
    return


# アラート情報のモニタリング
def AlertMonitoring():
    global alert_info, alert_invalidate_sec

    while True:
        t = time.perf_counter()
        # 開始時間を設定してなければ設定
        alert_info[np.where(alert_info[:,6] == -1)[0],6] = t
        # アラート情報のフラグを落とす
        alert_info[np.where(alert_info[:,6] < t - alert_invalidate_sec)[0],1] = 0
        time.sleep(0.3)


# 描画用画面クローズ時に警告が出ないようにする
def DisableAssert():
    wx.DisableAsserts()
    return


# Iniファイル読み込み
def ReadIni():
    global alert, name

    ini = configparser.ConfigParser()
    ini.read('tab.ini')

    alert = ini['DEFAULT']['alert']
    name = ini['DEFAULT']['name']
    return


##############################
#
# ここから本体
#
##############################

# Iniファイル読み込み
ReadIni()

# 味方のミニマップを初期化
img_g = np.array([False])

tabWnd = 0
start_time = time.perf_counter()

try:
    while True:

        # They Are Billions の画面が開いてない場合
        if win32gui.GetWindowText(tabWnd) != name:
            # Windowハンドルに依存する値の初期化を無効にする処理
            if tabWnd != 0:
                tabWnd = 0
                mmapDC.DeleteDC()
                dateDC.DeleteDC()
                win32gui.ReleaseDC(tabWnd, wndDC)
                win32gui.DeleteObject(mmapBMP.GetHandle())
                win32gui.DeleteObject(dateBMP.GetHandle())

            # They Are Billions の画面取得を試みる
            tabWnd = win32gui.FindWindow(None, name)

            # They Are Billions の画面を取得できれば初期化
            if tabWnd != 0:
                # Windowハンドルに依存する値を初期化する処理
                tab_left, tab_top, tab_right, tab_bottom = win32gui.GetWindowRect(tabWnd)

                # 画面サイズからミニマップの座標を計算
                mmap_top    = int( (tab_bottom - tab_top) * 7 / 9 )
                mmap_bottom = int( (tab_bottom - tab_top) * 0.99 )
                mmap_left   = (tab_bottom - tab_top) - mmap_bottom
                mmap_right  = mmap_left + (mmap_bottom - mmap_top)
                mmap_width  = mmap_right - mmap_left
                mmap_height = mmap_bottom - mmap_top

                # 画面サイズから日付の座標を計算
                date_top    = int( (tab_bottom - tab_top) * 7 / 8 )
                date_bottom = int( (tab_bottom - tab_top) * 10 / 11 )
                date_left   = int( (tab_right - tab_left) / 7 )
                date_right  = int( (tab_right - tab_left) / 6 )
                date_width  = date_right - mmap_left
                date_height = date_bottom - mmap_top

                alert_invalidate_range = int( (tab_bottom - tab_top) * 0.01)

                # DCを作成
                wndDC = win32gui.GetWindowDC(tabWnd)
                srcDC = win32ui.CreateDCFromHandle(wndDC)

                # ミニマップ用DCとビットマップを作成（画面の画像取得はまだ）
                mmapDC= srcDC.CreateCompatibleDC()
                mmapBMP = win32ui.CreateBitmap()
                mmapBMP.CreateCompatibleBitmap(srcDC, mmap_width, mmap_height)
                mmapDC.SelectObject(mmapBMP)

                # 日付用DCとビットマップを作成（画面の画像取得はまだ）
                dateDC = srcDC.CreateCompatibleDC()
                dateBMP = win32ui.CreateBitmap()
                dateBMP.CreateCompatibleBitmap(srcDC, date_width, date_height)
                dateDC.SelectObject(dateBMP)

                # このスレッド以外のスレッドがあれば、表示用ウィンドウの位置・サイズ変更
                if threading.active_count() > 1:
                    frame.SetSize(mmap_left, mmap_top, mmap_width, mmap_height)

                continue

            # They Are Billions の画面を取得できなければループ
            time.sleep(1)
            continue

        # 初期化
        if status == 0:

            # 描画用透明ウィンドウを作成・表示
            atexit.register(DisableAssert)
            t_Window = threading.Thread(target=OpenAppWindow)
            t_Window.start()

            # アラート監視スレッド作成・開始
            t_Monitor = threading.Thread(target=AlertMonitoring)
            t_Monitor.setDaemon(True)
            t_Monitor.start()

            # BGRで画像ファイルのイメージを取得
            img_start = cv2.imread('start_date.png')
            img_end   = cv2.imread('end_date.png')

            # 日付ファイルがなければ無条件にアラート監視を開始
            if img_start is None or img_end is None:
                img_start = None
                img_end = None
                alert_num = 0    # アラート番号を初期化

                status = 2
                continue

            # BGR -> RGB に変換
            img_start = cv2.cvtColor(img_start, cv2.COLOR_BGR2RGB)
            img_end   = cv2.cvtColor(img_end  , cv2.COLOR_BGR2RGB)

            # 状態遷移
            status = 1

        # 日付画像を取得
        dateDC.BitBlt((0, 0), (date_width, date_height), srcDC, (date_left, date_top), win32con.SRCCOPY)
        img_date = np.frombuffer(dateBMP.GetBitmapBits(True), np.uint8).reshape(date_height, date_width, 4)
        img_date = cv2.cvtColor(img_date, cv2.COLOR_BGRA2RGB)    # 元はBGRA

        # 監視前状態、初日が始まったらアラート監視に遷移する
        if status == 1:
            if IsMatch(img_date, img_start):
                alert_num = 0    # アラート番号を初期化
                status = 2
                if os.path.exists('start.wav'):
                    playsound.playsound('start.wav')

        # アラート監視、監視終了日になったら監視前状態に遷移する
        if status == 2:

            # ミニマップ画像を取得
            mmapDC.BitBlt((0, 0), (mmap_width, mmap_height), srcDC, (mmap_left, mmap_top), win32con.SRCCOPY)
            img_mmap = np.frombuffer(mmapBMP.GetBitmapBits(True), np.uint8).reshape(mmap_height, mmap_width, 4)
            img_mmap = cv2.cvtColor(img_mmap, cv2.COLOR_BGRA2RGB)    # 元はBGRA
            img_mmap = cv2.cvtColor(img_mmap, cv2.COLOR_RGB2HSV)

            # ミニマップから明るい赤を取得
            img_r = cv2.inRange(img_mmap, np.array([0,210,200], img_mmap.dtype), np.array([4,255,255], img_mmap.dtype))

            # ミニマップの明るい赤と緑を and で比較
            img_res = img_g & img_r
            
            # ミニマップから緑を取得。次のループで使う
            img_g = cv2.inRange(img_mmap, np.array([31,155,100], img_mmap.dtype), np.array([60,255,200], img_mmap.dtype))

            # ミニマップからアラート色を取得
            img_alert1 = cv2.inRange(img_mmap, np.array([0,135,140], img_mmap.dtype), np.array([35,255,255], img_mmap.dtype))
            img_alert2 = cv2.inRange(img_mmap, np.array([179,230,250], img_mmap.dtype), np.array([179,255,255], img_mmap.dtype))
            img_alert = img_alert1 | img_alert2
            contours, hierarchy = cv2.findContours(img_alert, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 一定サイズ以下を削除
            contours = list(filter(lambda x: cv2.contourArea(x) > alert_invalidate_range * alert_invalidate_range, contours))

            # 検知図形が4つ以上なら通常アラートかを確かめる
            if len(contours) >= 4:
                x = min( co[0] for co in (cv2.boundingRect( con ) for con in contours) )
                y = min( co[1] for co in (cv2.boundingRect( con ) for con in contours) )
                w = max( co[0] + co[2] for co in (cv2.boundingRect( con ) for con in contours) ) - x
                h = max( co[1] + co[3] for co in (cv2.boundingRect( con ) for con in contours) ) - y
                # 縦横比率誤差2%未満を正方形として通常アラートとして登録
                if 0.98 < w/h and w/h < 1.02:
                    # ミニマップ端に近い場合は切り捨て
                    if alert_invalidate_range*3 < x and x+w < mmap_width - alert_invalidate_range*3 and alert_invalidate_range*3 < y and y+h < mmap_height - alert_invalidate_range*3:
                        # 通常アラートをミニマップの判定に追加
                        img_res[int(y+h/2), int(x+w/2)] = 1

            # フラグが立ってないアラート情報を削除
            alert_info = np.delete(alert_info, np.where(alert_info[:,1] == 0)[0], axis=0)

            # フラグが立ってるアラート情報はミニマップの判定から削除する
            for alt in alert_info:
                img_res[alt[2]:alt[3], alt[4]:alt[5]] = 0

            if np.any(img_res):
                # アラートを鳴らす
                t = threading.Thread(target=PlayAlert)
                t.start()

                contours, hierarchy = cv2.findContours(img_res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for i in range(len(contours)):
                    # アラート情報に登録
                    alert_num = alert_num + 1
                    x, y, w, h = cv2.boundingRect(contours[i])
                    v = np.array([[alert_num, 1, max(y-alert_invalidate_range,0), min(y+h+alert_invalidate_range,mmap_height), max(x-alert_invalidate_range,0), min(x+w+alert_invalidate_range,mmap_width), -1]])
                    alert_info = np.append(alert_info, v, axis=0)

            # 監視終了日になったら監視前状態に遷移する
            if IsMatch(img_date, img_end):
                status = 1
                if os.path.exists('end.wav'):
                    playsound.playsound('end.wav')

            # 1処理1/60秒を目指して調整
            end_time = time.perf_counter()
            wait_time = base_wait_time - (end_time - start_time)
            if wait_time > 0:
                windll.winmm.timeBeginPeriod(1)
                time.sleep(wait_time)
                windll.winmm.timeEndPeriod(1)
            start_time = time.perf_counter()

# Ctrl + C で終了
except KeyboardInterrupt:
    windll.winmm.timeEndPeriod(1)

    if frame != None:
        frame.Close()
        frame.Destroy()

    t_Window.join()

    if tabWnd != 0:
        tabWnd = 0
        mmapDC.DeleteDC()
        dateDC.DeleteDC()
        srcDC.DeleteDC()
        win32gui.ReleaseDC(tabWnd, wndDC)
        win32gui.DeleteObject(mmapBMP.GetHandle())
        win32gui.DeleteObject(dateBMP.GetHandle())

    print('exit tab.py')
