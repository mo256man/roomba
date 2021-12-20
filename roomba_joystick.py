# pygameでゲーム中に動画を再生したい
# https://teratail.com/questions/193754

import statistics
import time
import numpy as np
import sys

import cv2
import pygame
from pygame.locals import *

import create


# OpenCVで動画を取り込む　カメラ映像の場合はカメラ番号を指定する
cap = cv2.VideoCapture(0)
#    cap = cv2.VideoCapture(0)
width, height = 1280, 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

class MySprite(pygame.sprite.Sprite):
    """pyagemsのスプライト処理"""
    def __init__(self, name, x, y, mv_x, mv_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(name).convert_alpha()        # 透過変換でファイル読み込み
        width  = self.image.get_width()
        height = self.image.get_height()
        self.rect = Rect(x, y, width, height)
        self.mv_x = mv_x
        self.mv_y = mv_y
 
    def update(self, mv_x, mv_y):
        self.rect.move_ip(mv_x, mv_y)                               # 移動描写
        self.rect = self.rect.clamp(Rect(0, 0, width, height) )     # 画面内に収める
   
    def draw(self, surface):
        surface.blit(self.image, self.rect)

def get_roomba_port():
    coms = serial.tools.list_ports.comports()                       # ポートデータ取得
    port = ""
    for com in coms:
        if "/dev/ttyUSB" in com.device:
            port = com.device
    return port


def main():
    # roomba
    ROOMBA_PORT = get_roomba_port()
    print (ROOMBA_PORT)
    robot = create.Create(ROOMBA_PORT)
    robot.printSensors() 
    robot._start()
    robot.toSafeMode()

    # ジョイスティックの初期化
    pygame.joystick.init()
    try:
        # ジョイスティックインスタンスの生成
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print('ジョイスティックの名前:', joystick.get_name())
        print('ボタン数 :', joystick.get_numbuttons())
    except pygame.error:
        print('ジョイスティックが接続されていません')

    # Pygameを初期化
    pygame.init()
    pygame.display.set_caption("OpenCV camera stream on Pygame")
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # スプライト
    x, y = width/2, height/2
    vx, vy = 0, 0
    roomba = MySprite("roomba.png", x, y, vx, vy)
    
    # 永久ループ
    try:
        while True:
            clock.tick(30)      #フレームレート

            for event in pygame.event.get():
                # print (event.type)                
                if event.type == JOYBUTTONDOWN:
                    print("joy down")
                    if event.button == 12: vy = -10     # up
                    if event.button == 13: vx = -30      # right
                    if event.button == 14: vy = 10      # down
                    if event.button == 15: vx = 30     # left
                    if event.button == 4: vx = 30      # L1
                    if event.button == 6: vx = -30       # R1

                if event.type == JOYBUTTONUP:
                    print("joy up")
                    if event.button == 12: vy = 0     # up
                    if event.button == 13: vx = 0      # right
                    if event.button == 14: vy = 0      # down
                    if event.button == 15: vx = 0     # left
                    if event.button == 4: vx = 0      # L1
                    if event.button == 6: vx = 0       # R1

                if event.type == KEYDOWN:
                    print("key down")
                    if event.key == K_LEFT:
                        vx = 30
                    if event.key == K_RIGHT:
                        vx = -30
                    if event.key == K_UP:
                        vy = -10
                    if event.key == K_DOWN:
                        vy = +10
                    if event.key == K_ESCAPE:
                        sys.exit(0)

                if event.type == KEYUP:
                    print("key up")
                    if event.key == K_LEFT:
                        vx = 0
                    if event.key == K_RIGHT:
                        vx = 0
                    if event.key == K_UP:
                        vy = 0
                    if event.key == K_DOWN:
                        vy = 0

#            print ((x,y))

            ret, frame = cap.read()
            if True:
                frame = np.full((320,240,3), (255,255,255), np.uint8)
#                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      # BGR -> RGB
#                frame = frame.swapaxes(0,1)                         # x軸y軸交換
                frame = pygame.surfarray.make_surface(frame)        # 以上の加工をした画像をpygameのサーフェスに取り込む
    #            screen.fill([0,0,0])                                # 画面を塗りつぶしてリセットする
            screen.blit(frame, (0,0))                           # スクリーン上に画像を描写する
    #        roomba.update(vx, vy)                               # スプライトを更新する
    #        roomba.draw(screen)                                 # スプライトを描写する
            pygame.display.update()                             # 画面更新する

            robot.go(-vy, vx) # forward

    except KeyboardInterrupt:
        pygame.quit()
        cv2.destroyAllWindows()
        robot.close()

    except SystemExit:
        pygame.quit()
        cv2.destroyAllWindows()
        robot.close()


if __name__ == '__main__':
    main()