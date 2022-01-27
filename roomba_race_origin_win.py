from pyroombaadapter import PyRoombaAdapter                 # ルンバを操作するライブラリ
#import create                                              # ルンバを操作するライブラリ
import time                                                 # 時間に関するライブラリ
import sys                                                  # システムに関するライブラリ
import serial.tools.list_ports                              # シリアル通信に関するライブラリ
import math                                                 # 数学に関するライブラリ
import numpy as np
import cv2
from simulator import Roomba_sim


def get_roomba_port():
    """
    シリアル接続のポート番号を取得する
    USBに一つだけつながっているという前提（複数あったら失敗する可能性あり）
    """
    port = ""                                               # ポートの初期値
    comports = serial.tools.list_ports.comports()           # ポートデータ取得
    for comport in comports:                                # 取得した個々のポートデータで
        if "COM" in comport.device:                         # "COM" という文字列がデバイスにあったら
            port = comport.device                           # それがルンバが接続されているポート
            ser = serial.Serial(port)                       # そのポートでのシリアル接続を
            ser.close()                                     # ルンバと接続する前にいったん切る
    
    if port == "":                                          # ルンバが見つからなかったら
        print("No roomba is found.")
        port = False                                        # ポートの値として空白でなくFalseとする

    return port                                             # ポートを返す

ROOMBA_PORT = get_roomba_port()                             # ルンバのポートを取得
print(ROOMBA_PORT)
if ROOMBA_PORT != False:
    robot = PyRoombaAdapter(ROOMBA_PORT)                        # そのポートでルンバを操作する
    robot.change_mode_to_safe()                                 # ルンバをセーフモードで起動する
sim = Roomba_sim(debug=False)

def stop():
    """
    ルンバを停止させる
    """
    if ROOMBA_PORT != False:
        robot.move(0, 0)                                        # 移動速度と旋回速度を0に指定することで停止させる
    
def robot_drive(right_mm_sec, left_mm_sec):
    if ROOMBA_PORT != False:
        robot.send_drive_direct(right_mm_sec, left_mm_sec)


def robot_turn(turn_speed):
    go_speed = turn_speed * 235.0 / 2
    if turn_speed>0:
        turn_speed = turn_speed
    else:
        turn_speed = turn_speed

    if ROOMBA_PORT != False:
        robot.send_drive_direct(go_speed, -go_speed)
    

def go(mm):                                                 # 距離はmmで指定する
    mm_per_sec = 500                                        # 暫定の移動速度（mm/sec）
    if mm < 0:                                              # 距離がマイナスならば
        mm_per_sec = -mm_per_sec                            # 移動速度をマイナスにする

    wait_sec = mm / mm_per_sec                              # 時間=距離÷速さ

    if ROOMBA_PORT != False:
        robot_drive(mm_per_sec, mm_per_sec)
        time.sleep(wait_sec)                                    # 指定した時間だけ待つ
        stop()                                                  # ルンバを止める

    sim.go(mm_per_sec, wait_sec)


def turn(angle_degree):                                     # 角度はdegreeで指定する
    angle_radian = 2 * math.pi / 360 * angle_degree         # 角度をradにする
    degree_per_sec = 90                                     # 暫定の旋回速度（degree/sec）
    rad_per_sec = 2 * math.pi / 360 * degree_per_sec        # 暫定の旋回速度をrad/secにする
    if angle_degree < 0:                                    # 旋回角度がマイナスならば
        rad_per_sec = -rad_per_sec                          # 旋回速度をマイナスにする

    wait_sec = angle_radian / rad_per_sec                   # 時間=距離÷速さ

    if ROOMBA_PORT != False:
        robot_turn(rad_per_sec)                                 # 移動速度はゼロ、旋回速度を設定してルンバを動かす
        time.sleep(wait_sec)                                    # 指定した時間だけ待つ
        stop()                                                  # ルンバを止める

    sim.turn(rad_per_sec, wait_sec)

# ここから下にルンバで迷路を脱出するコードを書く
# 以下は例
go(500)
turn(90)
go(500)
turn(90)
go(500)
turn(90)
go(500)
turn(90)

# 最後に、ルンバとの通信を切る
if ROOMBA_PORT != False:
    del robot

# シミュレーターを終了させる
sim.end()
