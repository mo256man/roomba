from pyroombaadapter import PyRoombaAdapter                 # ルンバを操作するライブラリ
#import create                                              # ルンバを操作するライブラリ
import time                                                 # 時間に関するライブラリ
import sys                                                  # システムに関するライブラリ
import serial.tools.list_ports                              # シリアル通信に関するライブラリ
import math                                                 # 数学に関するライブラリ

def get_roomba_port():
    """
    シリアル接続のポート番号を取得する
    USBに一つだけつながっているという前提（複数あったら失敗する可能性あり）
    """
    port = ""                                               # ポートの初期値
    comports = serial.tools.list_ports.comports()           # ポートデータ取得
    for comport in comports:                                # 取得した個々のポートデータで
        if "/dev/ttyUSB" in comport.device:                 # "/dev/ttyUSB" という文字列がデバイスにあったら
            port = comport.device                           # それがルンバが接続されているポート
            ser = serial.Serial(port)                       # そのポートでのシリアル接続を
            ser.close()                                     # ルンバと接続する前にいったん切る
    
    if port == "":                                          # ルンバが見つからなかったら
        print("ルンバが見つかりません")                             # メッセージを表示して
        sys.exit()                                          # プログラムを中断する

    return port                                             # ポートを返す

ROOMBA_PORT = get_roomba_port()                             # ルンバのポートを取得
robot = PyRoombaAdapter(ROOMBA_PORT)                        # そのポートでルンバを操作する
robot.change_mode_to_safe()                                 # ルンバをセーフモードで起動する


def stop():
    """
    ルンバを停止させる
    """
    robot.move(0, 0)                                        # 移動速度と旋回速度を0に指定することで停止させる
    
def robot_drive(right_mm_sec, left_mm_sec):
    robot.send_drive_direct(right_mm_sec, left_mm_sec)


def robot_turn(turn_speed):
    go_speed = turn_speed * 235.0 / 2
    if turn_speed>0:
        turn_speed = turn_speed
    else:
        turn_speed = turn_speed
    robot.send_drive_direct(go_speed, -go_speed)
    

def go(distance):
    """
    ルンバを直進させる
    distance: 距離(m)
    """
    go_speed = 200                                          # 移動速度（mm/sec）
    if distance < 0:                                        # 距離がマイナスならば
        go_speed = -go_speed                                # 移動速度をマイナスにする

    
#    robot.move(go_speed, 0)                                 # 旋回速度はゼロ、移動速度を設定してルンバを動かす
    robot_drive(go_speed, go_speed)
    wait_time = distance / go_speed                         # 時間=距離÷速さ
    time.sleep(wait_time)                                   # 指定した時間だけ待つ
    stop()                                                  # ルンバを止める


def turn(angle_degree):
    """
    ルンバをその場で旋回させる
    angle_degree: 旋回角度（度）　反時計回りが正、時計回りが負
    """
    #angle_degree = angle_degree/1.21                        # 右と左のモーターの強さが違うので調整
    turn_speed = 2 * math.pi / 360 * 45                     # 旋回速度（rad/sec）
    if angle_degree < 0:                                    # 旋回角度がマイナスならば
        turn_speed = -turn_speed                            # 旋回速度をマイナスにする
        
    angle_radians = 2 * math.pi / 360 * angle_degree        # 旋回角度　度からラジアンにする
    robot_turn(turn_speed)                                  # 移動速度はゼロ、旋回速度を設定してルンバを動かす
    wait_time = angle_radians / turn_speed                  # 時間=距離÷速さ
    time.sleep(wait_time)                                   # 指定した時間だけ待つ
    stop()                                                  # ルンバを止める



# ここから下にルンバで迷路を脱出するコードを書く
# 以下は例
turn(-180)


# 最後に、ルンバとの通信を切る
del robot