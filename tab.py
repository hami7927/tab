import cv2
import numpy as np
import win32gui
import playsound
from PIL import ImageGrab
import configparser


mmap_top = 830
alert = 'alert.mp3'
name = 'They Are Billions'


def GetWindowImg():
    try :
        global name

        handle = win32gui.FindWindow(None, name)
        if handle == 0:
            return np.array([False])
        rect = win32gui.GetWindowRect(handle)
        img = ImageGrab.grab(rect)
        img = np.asarray(img)
        return img
    except IndexError as e:
        return np.array([False])


def CutMiniMapRect(img):
    global mmap_top

    h, w, d = img.shape
    return img[mmap_top:, :h - mmap_top]


def Alert():
    global alert

    playsound.playsound(alert)
    return


def ReadIni():
    ini = configparser.ConfigParser()
    ini.read('tab.ini')

    global mmap_top
    global alert
    global name

    mmap_top = int(ini['DEFAULT']['top'])
    alert = ini['DEFAULT']['alert']
    name = ini['DEFAULT']['name']
    return


ReadIni()
g_img = np.array([False])

try:
    while True:
        img = GetWindowImg()
        if img.size == 1:
            continue

        m_img = CutMiniMapRect(img)
        r_img = cv2.inRange(m_img, np.array([200,0,0], np.uint8), np.array([255,100,100], np.uint8))
        res_img = g_img & r_img
        g_img = cv2.inRange(m_img, np.array([0,100,0], np.uint8), np.array([100,255,100], np.uint8))
        if np.any(res_img):
            Alert()

except KeyboardInterrupt:
    print('exit tab.py')
