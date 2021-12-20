import create
import time
import datetime
import sys
import random
import serial.tools.list_ports

def get_roomba_port():
    coms = serial.tools.list_ports.comports()                       # ポートデータ取得
    port = ""
    for com in coms:
        if "/dev/ttyUSB" in com.device:
            port = com.device
    
    if port == "":
        print("no roomba found")
        sys.exit()
    return port
    


def main():
    ROOMBA_PORT = get_roomba_port()
    print (ROOMBA_PORT)
    
    robot = create.Create(ROOMBA_PORT)
    
    robot._start()
    robot.toSafeMode()    
#    robot.toFullMode() # dont stop    
    
#    robot.printSensors() 

    while True:
        
        if robot.getMode() != create.SAFE_MODE:
            sys.exit()
            
        #print(datetime.datetime.now(), "CLIFF_FRONT_LEFT", robot.senseFunc(create.CLIFF_FRONT_LEFT)()) 

        if not (robot.senseFunc(create.LEFT_BUMP)() or robot.senseFunc(create.RIGHT_BUMP)()):
            print("go foward")
            robot.go(10, 0)
        else:
            print("back and turn")
            robot.stop()
            time_end = time.time() + 1  # sec
            while time.time() < time_end:
                robot.go(-10, 0)

            sign = random.randint(0,1)*2-1      # -1 0r 1
            time_end = time.time() + 1  # sec
            while time.time() < time_end:
                robot.go(0, sign*45)

        
        time.sleep(0.1)
    
    
if __name__ == "__main__":
    main()
