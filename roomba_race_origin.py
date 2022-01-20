from pyroombaadapter import PyRoombaAdapter
#import create
import time
import datetime
import sys
import random
import serial.tools.list_ports
import math

ROOMBA_PORT = get_roomba_port()                             # ルンバのポートを取得
robot = PyRoombaAdapter(ROOMBA_PORT)                        # そのポートでルンバを操作する
robot.change_mode_to_safe()    


def get_roomba_port():
    """
    シリアル接続のポート番号を取得する　USBに一つだけつながっているという前提
    """
    comports = serial.tools.list_ports.comports()           # ポートデータ取得
    port = ""                                               # ポートの初期値
    for comport in comports:                                # 取得した個々のポートデータにおいて
        if "/dev/ttyUSB" in comport.device:                 # "/dev/ttyUSB" という文字列がデバイスにあったら
            port = comport.device                           # それがルンバが接続されているポート
            ser = serial.Serial(port)
            ser.close()
                                                            
    
    if port == "":                                          # ルンバが見つからなかったら
        print("ルンバが見つかりません")                     # メッセージを表示して
        sys.exit()                                          # プログラムを中断する
    return port


def stop():
    robot.move(0, 0)  # stop
    

def go(distance):
    """
    go for x m
    """
    go_speed = 0.2              # m/sec
    if distance < 0:
        go_speed = -go_speed
    robot.move(go_speed, 0)  # go straight
    wait_time = distance / go_speed         # sec
    time.sleep(wait_time)
    stop()



def turn(angle_degree):
    """
    turn x degree
    """
    angle_degree = angle_degree/1.21
    turn_speed = 2 * math.pi / 360 * 45                # rad/sec
    if angle_degree < 0:
        turn_speed = -turn_speed
        
    angle_radians = 2 * math.pi / 360 * angle_degree
    robot.move(0, turn_speed)  # go straight
    wait_time = angle_radians / turn_speed
    time.sleep(wait_time)
    stop()



  
# ここから下にルンバで迷路を脱出するコードを書く
go(0.5)
turn(180)
go(0.5)
turn(-180)

#
del robot
