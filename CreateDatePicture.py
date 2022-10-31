import sys
import cv2
import numpy as np

#
# 使い方
# python CreateDatePicture.py infile1 infile2
#
# 入力
# infile1 : アラート対策開始日をキャプチャした画像ファイル（無劣化pngファイル）。 0日目をキャプチャした画像ファイルを推奨
# infile2 : アラート対策終了日をキャプチャした画像ファイル（無劣化pngファイル）。20日目をキャプチャした画像ファイルを推奨
#
# 出力
# start_date.png, end_date.png を出力する
#


def CutDateRect(img):
    img_h, img_w, img_d = img.shape
    top    = int(img_h*7/8)
    bottom = int(img_h*10/11)
    left   = int(img_w/7)
    right  = int(img_w/6)

    return img[top:bottom,left:right]


args = sys.argv
if 3 != len(args):
    print('use like : CreateDatePicture.py infileStart infileEnd')
    quit()

if not args[1].isascii():
    print('1st Argument is not ascii ' + args[1])
    quit()

if not args[2].isascii():
    print('2nd Argument is not ascii ' + args[1])
    quit()

i_file_start = args[1]
i_file_End = args[2]
o_file_start = "start_date.png"
o_file_End = "end_date.png"

try:

    img = cv2.imread(i_file_start)
    d_img = CutDateRect(img)
    cv2.imwrite(o_file_start, d_img)

    img = cv2.imread(i_file_End)
    d_img = CutDateRect(img)
    cv2.imwrite(o_file_End, d_img)

except KeyboardInterrupt:
    print('exit CreateDatePicture.py')

