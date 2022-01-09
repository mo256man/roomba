import create
import time
import datetime
import sys
import random
import serial.tools.list_ports

"""
ルンバを動かす
    robot.go(cm_per_sec=, deg_per_sec)
        cm_per_sec…
        deg_per_sec…


    robot.stop()
        ルンバを停止する
        内部的にrobot.go(0,0)と同じ

    

"""


def get_roomba_port():
    """
    シリアル接続のポート番号を取得する　USBに一つだけつながっているという前提
    """
    comports = serial.tools.list_ports.comports()           # ポートデータ取得
    port = ""                                               # ポートの初期値
    for comport in comports:                                # 取得した個々のポートデータにおいて
        if "/dev/ttyUSB" in comport.device:                 # "/dev/ttyUSB" という文字列がデバイスにあったら
            port = comport.device                           # それがルンバが接続されているポート
    
    if port == "":                                          # ルンバが見つからなかったら
        print("ルンバが見つかりません")                           # メッセージを表示して
        sys.exit()                                          # プログラムを中断する
    return port
    


def main():
    ROOMBA_PORT = get_roomba_port()                         # ルンバのポートを取得
    robot = create.Create(ROOMBA_PORT)                      # そのポートでルンバを操作する
    
    robot._start()                                          # ルンバ起動
    robot.toSafeMode()                                      # セーフモードにする
#    robot.toFullMode()                                     # 持ち上げても止まらないフルモードにするにはこちら
    
#    robot.printSensors() 

    while True:                                             # 無限ループ
        
        if robot.getMode() != create.SAFE_MODE:             # セーフモードでなくなったら
            robot.stop()                                    # ロボットを停止して
            sys.exit()                                      # プログラムを中断する
        
        # ここから下にルンバで迷路を脱出するコードを書く
            
         

        time.sleep(0.1)                                     # 0.1秒停止する


if __name__ == "__main__":
    main()