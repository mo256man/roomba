#from pyroombaadapter import PyRoombaAdapter                 # ルンバを操作するライブラリ
#import create                                              # ルンバを操作するライブラリ
import time                                                 # 時間に関するライブラリ
import sys                                                  # システムに関するライブラリ
import serial.tools.list_ports                              # シリアル通信に関するライブラリ
import math                                                 # 数学に関するライブラリ
import numpy as np
import platform
from simulator import Roomba_sim


def get_roomba_port():
    """
    シリアル接続のポート番号を取得する
    一つだけつながっているという前提（複数あったら最後の一つを取得する仕様につき失敗する可能性あり）
    """
    os = platform.system()                                  # OSを取得する
    if os == "Windows":                                     # Windowsの場合の
        port_str = "COM"                                    # ポートを探す文字列
    elif os == "Linux":                                     # Linuxの場合の
        port_str = "/dev/ttyUSB"                            # ポートを探す文字列
    else:                                                   # それ以外の場合の
        port_str = "unknown OS"                             # ポートを探す文字列

    port = ""                                               # ポートの初期値
    comports = serial.tools.list_ports.comports()           # ポートデータ取得
    for comport in comports:                                # 取得した個々のポートデータで
        if port_str in comport.device:                      # ポートを探す文字列がデバイスにあったら
            port = comport.device                           # それがルンバが接続されているポート
            ser = serial.Serial(port)                       # そのポートでのシリアル接続を
            ser.close()                                     # ルンバと接続する前にいったん切る
    
    if port == "":                                          # ルンバが見つからなかったら
        print("No roomba is found.")                        # メッセージを表示する
        port = False                                        # ポートの値として空白でなくFalseとする

    return port                                             # ポートを返す


"""
ここはメイン（robotとsimをグローバル変数として扱う）
"""
ROOMBA_PORT = get_roomba_port()                             # ルンバのポートを取得

if ROOMBA_PORT != False:                                    # ポートが見つかっていたら
    robot = PyRoombaAdapter(ROOMBA_PORT)                    # そのポートでルンバを操作する
    robot.change_mode_to_safe()                             # ルンバをセーフモードで起動する

sim = Roomba_sim(save_anim=True)                               # クラス「Roomba_sim」を使う


"""
以下、関数定義
"""
def stop():
    """
    ルンバを停止させる
    """
    if ROOMBA_PORT != False:
        robot.move(0, 0)                                    # 移動速度と旋回速度を0に指定することで停止させる
    
def robot_drive(right_mm_sec, left_mm_sec):
    """
    PyRoombaAdapterでルンバを動かす
    """
    if ROOMBA_PORT != False:
        robot.send_drive_direct(right_mm_sec, left_mm_sec)


def robot_turn(turn_speed):
    """
    PyRoombaAdapterでルンバをその場旋回させる
    """
    go_speed = turn_speed * 235.0 / 2
    if turn_speed>0:
        turn_speed = turn_speed
    else:
        turn_speed = turn_speed

    if ROOMBA_PORT != False:
        robot.send_drive_direct(go_speed, -go_speed)
    

def go(mm):                                                 # 距離はmmで指定する
    """
    ルンバを走行させる
    """
    mm_per_sec = 500                                        # 暫定の移動速度（mm/sec）
    if mm < 0:                                              # 距離がマイナスならば
        mm_per_sec = -mm_per_sec                            # 移動速度をマイナスにする

    wait_sec = mm / mm_per_sec                              # 時間=距離÷速さ

    if ROOMBA_PORT != False:
        robot_drive(mm_per_sec, mm_per_sec)
        time.sleep(wait_sec)                                # 指定した時間だけ待つ
        stop()                                              # ルンバを止める

    command = f"go({round(mm_per_sec,2)}, {wait_sec})"      # シミュレーターに送るコマンド文字列
    sim.go(mm_per_sec, wait_sec, command)                   # 指定した速度・待ち時間でシミュレーターを走らせる


def turn(angle_degree):                                     # 角度はdegreeで指定する
    angle_radian = 2 * math.pi / 360 * angle_degree         # 角度をradにする
    degree_per_sec = 90                                     # 暫定の旋回速度（degree/sec）
    rad_per_sec = 2 * math.pi / 360 * degree_per_sec        # 暫定の旋回速度をrad/secにする
    if angle_degree < 0:                                    # 旋回角度がマイナスならば
        rad_per_sec = -rad_per_sec                          # 旋回速度をマイナスにする

    wait_sec = angle_radian / rad_per_sec                   # 時間=距離÷速さ

    if ROOMBA_PORT != False:
        robot_turn(rad_per_sec)                             # 移動速度はゼロ、旋回速度を設定してルンバを動かす
        time.sleep(wait_sec)                                # 指定した時間だけ待つ
        stop()                                              # ルンバを止める

    command = f"turn({round(rad_per_sec,2)}, {wait_sec})"   # シミュレーターに送るコマンド文字列
    sim.turn(rad_per_sec, wait_sec, command)                # 指定した速度・待ち時間でシミュレーターを走らせる

# ここから下にルンバで迷路を脱出するコードを書く
# 以下は例
go(700)
turn(-65)
go(700)
turn(65)
go(550)
turn(90)
go(500)

# 最後に、ルンバとの通信を切る
if ROOMBA_PORT != False:
    del robot

# シミュレーターを終了させる
sim.end()
