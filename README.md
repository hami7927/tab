# They Are Billions アラートバグ対策ツール
They Are Billionsのアラートバグ対策ツール。ミニマップを監視し、攻撃を検知した場合アラート用の音源を鳴らします。
  
  
# 設定

## tab.iniの編集
tab.iniをメモ帳等のエディタで開きます。
They Are Billions の解像度に対応した値に top 項目を編集する必要があります。

| 解像度 |topの値 |
----|---- 
| 1360x768 | 589 |
| 1920x1080 | 830 |
| 3840x2160 | 1660 |

top 項目は、ミニマップの上端が画面最上から何ドットかを意味します。They Are Billionsをウィンドウモードでプレイする場合、メニューバーの幅分topの値を加算してください。
開発環境ではフルスクリーン、解像度1920x1080以外は確認できていません。

name 項目は編集の必要はありません。

alert 項目はアラート用の音源ファイル名になります。 wav ファイルを利用する等ファイル名を変える必要がある
場合は変更してください。**<font color="Red">日本語ファイル名は利用できません、ツールが落ちます</font>**。

## アラート用ファイルの配置
フリー素材等からアラートに用いるファイルをダウンロードし tab.py 、 ~~tab.exe 、~~ tab.ini と同じフォルダに配置します。
ファイル名は tab.ini の alert 項目に設定したファイル名とします。
アラート用ファイルは再生時間の短いものを推奨します。アラートが終わるまで、次のアラートは鳴りません。

## python.pyを利用する場合
pythonをインストールします。開発環境は 3.9.7 を利用しました。

以下のpipコマンドでライブラリをインストールします  
pip install cv2  
pip install numpy  
pip install pyws  
pip install pywin32  
pip install playsound==1.2.2  
pip install Pillow  
pip install configparser  

各ライブラリの用途は以下の通りです。
|ライブラリ|用途|
----|---- 
|cv2|画像処理|
|numpy|cv2での画像格納|
|pyws|window id 扱うため|
|pywin32|win32guiを利用するため|
|playsoud|wav,mp3を鳴らすため。最新版（1.3.0）だとファイルロード時に落ちた|
|Pillow|ImageGrab を使うため|
|configparser|iniファイルの読み込み|
  
  
# プログラムの起動
起動は They Are Billions の起動前、起動中どちらでも構いません。

## ~~exeファイルを利用する場合~~
~~tab.exeをダブルクリックするとコマンドプロンプトが立ち上がり起動します。~~
~~コマンドプロンプトでtab.exeの存在するフォルダに移動後、以下のコマンドでも起動します。~~
> ~~tab.exe~~

## python スクリプトを利用する場合
コマンドプロンプトでtab.pyの存在するフォルダに移動します。
以下のコマンドで起動します。
> python tab.py
  
  
# プログラムの停止方法
コマンドプロンプトで「Ctrl c」で停止します。
停止は They Are Billions の起動中、停止後どちらでも構いません。
  
  
# 制限
- アラート用ファイルのファイル名に日本語ファイル名は利用できません
- アラート用ファイルは wav か mp3 に限ります
- エクスプローラーで「They Are Billions」という名前のフォルダを開いていると正常に動作しません
- ミニマップの白枠の白色部分は攻撃を検知できません
- 腐食の地以外のマップでは動作不良が起きる可能性があります。開発環境で試していません
- 1920x1080、フルスクリーン以外の環境で試していません
- 変異体、ジャイアントの攻撃検知は行われません
- アラートはゲームのアラートと同時か一呼吸遅れて鳴ります
  
  
# 動作原理
まだ書いてません
