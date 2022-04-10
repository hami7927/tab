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

try:
    while True:
        img = GetWindowImg()
        if img.size == 1:
            continue
        else:
            h, w, d = img.shape
            with open('tab_env.txt', mode='w') as f:
                f.write('{}x{}'.format(w,h))
            m_img = CutMiniMapRect(img)
            img = cv2.cvtColor(m_img, cv2.COLOR_BGR2RGB)
            cv2.imwrite('tab_env.png', img)

except KeyboardInterrupt:
    print('exit tab_env')
