# pygameでゲーム中に動画を再生したい
# https://teratail.com/questions/193754

import statistics
import time
import numpy as np
import sys

import cv2
import pygame
from pygame.locals import *


# OpenCVで動画を取り込む　カメラ映像の場合はカメラ番号を指定する
cap = cv2.VideoCapture("movie.mp4")
#    cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


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


def main():
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
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        vx = -10
                    if event.key == K_RIGHT:
                        vx = 10
                    if event.key == K_UP:
                        vy = -10
                    if event.key == K_DOWN:
                        vy = +10
                    if event.key == K_ESCAPE:
                        sys.exit(0)

                if event.type == KEYUP:
                    if event.key == K_LEFT:
                        vx = 0
                    if event.key == K_RIGHT:
                        vx = 0
                    if event.key == K_UP:
                        vy = 0
                    if event.key == K_DOWN:
                        vy = 0

            print ((x,y))

            ret, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      # BGR -> RGB
            frame = frame.swapaxes(0,1)                         # x軸y軸交換
            frame = pygame.surfarray.make_surface(frame)        # 以上の加工をした画像をpygameのサーフェスに取り込む
#            screen.fill([0,0,0])                                # 画面を塗りつぶしてリセットする
            screen.blit(frame, (0,0))                           # スクリーン上に画像を描写する
            roomba.update(vx, vy)                               # スプライトを更新する
            roomba.draw(screen)                                 # スプライトを描写する
            pygame.display.update()                             # 画面更新する

    except KeyboardInterrupt:
        pygame.quit()
        cv2.destroyAllWindows()

    except SystemExit:
        pygame.quit()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()