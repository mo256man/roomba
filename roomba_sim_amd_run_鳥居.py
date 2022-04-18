import time                                                 # 時間に関するライブラリ
import sys                                                  # システムに関するライブラリ
import math                                                 # 数学に関するライブラリ
import numpy as np                                          # 数値計算に関するライブラリ
from komono.simulator import Roomba_sim                            # 森島が作ったルンバシミュレーター
import configparser

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

sim = Roomba_sim(filename="coms.png")                       # ルンバシミュレーターを使う


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


def go(mm, run_speed):                                                         # 【引数】 [mm]走行させたい距離（㎜）　[run_speed]走行速度（㎜／ｓ）
    mm_per_sec = run_speed * spd_acc_go                                        # 移動速度（mm/sec）をセット＠＠＠
    if mm < 0:                                                                 # 後退か判断＠＠＠
       mm_per_sec = mm_per_sec * -1                                            # 後退ならマイナスにする＠＠＠
       
    wait_sec = abs(mm) / abs(mm_per_sec)                                       # 時間=距離÷速さ マイナスは計算できないので絶対値出す＠＠＠
    if ROOMBA_PORT != False:                                                   # 実際にルンバと接続していたら
        robot_go(mm_per_sec)                                                   # 走行スピードを設定してルンバを走らせる
        time.sleep(wait_sec)                                                   # 指定した時間だけ待つ
        stop()                                                                 # ルンバを止める

    command = f"go({round(mm_per_sec,2)}, {wait_sec})"                         # シミュレーターに送るコマンド文字列
    command = ''
    sim.go(mm_per_sec, wait_sec, command)                                      # 指定した速度＆方向・待ち時間でシミュレーターを走らせる


def turn(angle_degree, angle_Speed):                                           # 角度はdegreeで指定する 【引数】 [angle_degree]旋回させたい角度（°）　[angle_speed]走行速度（㎜／ｓ）
    Cnst_Rad = 57.3                                                            # １ラジアン=57.3°なので、定数を定義＠＠＠
    rad_per_sec =  angle_Speed * spd_acc_turn / Cnst_Rad                       # 旋回速度をラジアンで算出＠＠＠
    if angle_degree < 0:                                                       # 時計回りか判断＠＠＠
        rad_per_sec = rad_per_sec * -1                                         # 時計回りならマイナスにする＠＠＠
    
    wait_sec = abs(angle_degree) / (angle_Speed * spd_acc_turn)                # 旋回中の待ち時間を算出＠＠＠マイナスにならないように！
    if ROOMBA_PORT != False:                                                   # 実際にルンバと接続していたら
        robot_turn(rad_per_sec)                                                # 旋回スピードを設定してルンバを旋回させる
        time.sleep(wait_sec)                                                   # 指定した時間だけ待つ
        stop()                                                                 # ルンバを止める

    command = f"turn({round(rad_per_sec,16)}, {wait_sec})"                     # シミュレーターに送るコマンド文字列
    command = ''
    sim.turn(rad_per_sec, wait_sec, command)                                   # 指定した速度＆旋回方向・待ち時間でシミュレーターを走らせる


"""*******************************************************************
## 処理開始
*******************************************************************"""
"""****************************************
## 初期処理(Initialize)
****************************************"""
setup_ini = configparser.ConfigParser()
setup_ini.read('komono/setup.ini',encoding='utf-8')                            # iniファイルの呼び出し

# ドーピング
spd_acc_go   = float(setup_ini['accelerator']['go'])                           # go用の加速パラメータ抽出
spd_acc_turn = float(setup_ini['accelerator']['turn'])                         # turn用の加速パラメータ抽出

route_name = setup_ini['route']['fname']                                       # ルートファイル入力先格納抽出

"""****************************************
## 走行開始(Run)
****************************************"""
Route_data = open(route_name, 'r', encoding='utf-8')                           # ルートファイルを入力
RT_data = Route_data.readlines()                                               # ルートデータを丸ごと抽出

for RT_List in RT_data:                                                        # ルートデータEofになるまで繰り返し
    RT = RT_List.split(',')                                                    # パラメータをカンマで区切る
    if   RT_List[0] == '*':                                                    # '＊'はコメント行でスルー
        pass
    elif (RT_List == '\n') or (RT_List.strip() == ''):                         # 改行だけ ＆ スペースだけの行はスルー
        pass
    elif (RT_List == 'end\n') or (RT_List == 'end'):                           # 'end'以降は処理しない
        break
    elif RT[1] == 'go':                                                        # 'go'の時
        go( float(RT[2]), abs(float(RT[2])) )
    elif RT[1] == 'turn':                                                      # 'turn'の時
        turn( float(RT[2]), abs(float(RT[2])) )

Route_data.close()

# 終了処理
if ROOMBA_PORT != False:                                    # 実際にルンバと接続していたら
    del robot                                               # ルンバとの接続を切る
sim.end()                                                   # シミュレーターの画面を5秒後に閉じる
