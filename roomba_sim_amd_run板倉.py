import time                                                 # 時間に関するライブラリ
import sys                                                  # システムに関するライブラリ
import math                                                 # 数学に関するライブラリ
import numpy as np                                          # 数値計算に関するライブラリ
from komono.simulator import Roomba_sim                            # 森島が作ったルンバシミュレーター

# 以下はシミュレーターでは使わない
# import platform                                             # OSを調べるためのライブラリ
# import serial.tools.list_ports                              # シリアル通信に関するライブラリ


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
#ROOMBA_PORT = get_roomba_port()                             # ルンバのポートを取得する関数を使わないで
ROOMBA_PORT = False                                         # 強制的にルンバは動かさないモードにする
if ROOMBA_PORT != False:                                    # ポートが見つかっていたら
    from komono.pyroombaadapter import PyRoombaAdapter      # ルンバを操作するライブラリ
    robot = PyRoombaAdapter(ROOMBA_PORT)                    # そのポートでルンバを操作する
    robot.change_mode_to_safe()                             # ルンバをセーフモードで起動する

sim = Roomba_sim()                                          # ルンバシミュレーターを使う


"""
以下、関数定義
"""
def stop():
    # ルンバを停止させる
    robot.move(0, 0)                                        # 移動速度と旋回速度を0にすることで停止させる


def robot_go(right_mm_sec):
    # PyRoombaAdapterでルンバを動かす
    robot.move(right_mm_sec, 0)                             # 移動速度を設定し旋回速度をゼロにすることで直進させる


def robot_turn(turn_speed):
    # PyRoombaAdapterでルンバをその場旋回させる
    robot.move(0, turn_speed)                               # 移動速度をゼロにし旋回速度を設定することでその場旋回させる


def go(mm):                                                 # 距離はmmで指定する
    # ルンバを走行させる
    # これだけでは不十分なので正しく動くように書く
    mm_per_sec = 500                                        # 暫定の移動速度（mm/sec）
    wait_sec = mm / mm_per_sec                              # 時間=距離÷速さ
    if ROOMBA_PORT != False:                                # 実際にルンバと接続していたら
        robot_go(mm_per_sec)                                # 走行スピードを設定してルンバを走らせる
        time.sleep(wait_sec)                                # 指定した時間だけ待つ
        stop()                                              # ルンバを止める

    command = f"go({round(mm_per_sec,2)}, {wait_sec})"      # シミュレーターに送るコマンド文字列
    sim.go(mm_per_sec, wait_sec, command)                   # 指定した速度・待ち時間でシミュレーターを走らせる


def turn(angle_degree):                                     # 角度はdegreeで指定する
    # ルンバを旋回させる
    # これだけでは不十分なので正しく動くように書く
    rad_per_sec = 90                                        # 旋回速度（rad/sec）
    wait_sec = angle_degree / rad_per_sec                   # 待ち時間を計算する　ラジアンと度が混在してるぞ？
    if ROOMBA_PORT != False:                                # 実際にルンバと接続していたら
        robot_turn(rad_per_sec)                             # 旋回スピードを設定してルンバを旋回させる
        time.sleep(wait_sec)                                # 指定した時間だけ待つ
        stop()                                              # ルンバを止める

    command = f"turn({round(rad_per_sec,2)}, {wait_sec})"   # シミュレーターに送るコマンド文字列
    sim.turn(rad_per_sec, wait_sec, command)                # 指定した速度・待ち時間でシミュレーターを走らせる


# 関数を呼び出してルンバを動かす
go(200)     # 500mm前進する
turn(60)    # 反時計回りに90度旋回する
go(300)     # 500mm前進する
turn(40)    # 反時計回りに90度旋回する
go(400)     # 500mm前進する
turn(-70)   # 時計回りに90度旋回する
go(-700)    # 500mm後退する（数値がマイナス）
turn(-40)   # 時計回りに90度旋回する

# 終了処理
if ROOMBA_PORT != False:                                    # 実際にルンバと接続していたら
    del robot                                               # ルンバとの接続を切る
sim.end()                                                   # シミュレーターの画面を5秒後に閉じる
