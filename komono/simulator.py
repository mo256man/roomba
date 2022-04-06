import cv2
import numpy as np
import math
import sys
from PIL import Image
import csv

class Roomba_sim():
    # スケール　ルンバの直径は34cm、ルンバ画像のサイズは340*340。つまりスケール1だと1cm=10ピクセルとなる　

    def __init__(self, scale=0.25, width=800, height=800, debug=False, filename="roomba.png", coursename="course.csv", save_anim=False):
        if debug:
            self.wait_cv_time = 0
        else:
            self.wait_cv_time = 50
            
        self.name = "Roomba Simulator"
        self.scale = scale
        self.timer = 0
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.save_anim = save_anim
        self.imgs = []

        # マップ作成
        self.load_map(coursename)

        # 初期値
        self.x = 0
        self.y = 0
        self.angle = -90 * 2 * math.pi / 360

        # ルンバ画像
        filename = "komono/" + filename
        image = cv2.imread(filename, -1)
        image = cv2.resize(image, None, fx=scale, fy=scale)
        self.rx = image.shape[0]//2
        self.ry = image.shape[1]//2
        cv2.line(image, (self.rx, 0), (self.rx, 2*self.ry), (0,0,255,255), 1)
        cv2.line(image, (0, self.ry), (2*self.rx, self.ry), (0,0,255,255), 1)
        self.roomba = image
        self.putRoomba(t=0)

        cv2.imshow(self.name, self.screen)


    def putRoomba(self, t=0, command=""):
        # マップに軌跡を残す
        cv2.circle(self.screen, (int(self.x+self.gx), int(self.y+self.gy)), 5, (0,0,255), -1)
        cv2.circle(self.screen, (int(self.x+self.gx), int(self.y+self.gy)), self.ry, (0,0,255), 1)

        # マップにルンバを重ね書きする
        img = putSprite(self.screen.copy(), self.roomba, (self.x+self.gx,self.y+self.gy), self.angle, (self.rx, self.ry))

        # マップにルンバの座標を描写する
        sx = round(self.x/self.scale, 1)
        sy = round(-self.y/self.scale, 1)
        rad = round(self.angle, 2)
        deg = round(self.angle * 360 / (2*math.pi), 2)
        """
        cv2.putText(img, f"(x, y)=({sx}, {sy})", (10, 100), self.font, 1, (0,0,0), 2)
        cv2.putText(img, f"angle={rad}[rad]={deg}[degree]", (10, 150), self.font, 1, (0,0,0), 2)
        cv2.putText(img, f"command={command}", (10, 200), self.font, 1, (0,0,0), 2)
        cv2.putText(img, f"time={round(t/10, 1)}[sec]", (10, 250), self.font, 1, (0,0,0), 2)
        """
        cv2.imshow(self.name, img)
        self.imgs.append(img)
        key = cv2.waitKey(self.wait_cv_time) & 0xFF
        if key == 27:
            cv2.destroyAllWindows()
            sys.exit()

    def stop(self):
        self.putRoomba(self.timer)


    def go(self, mm_per_sec, wait_sec, command=""):
        # 0.1秒刻みで動くので、走行スピードはcm_per_secの1/10となる
        t = 0
        v = mm_per_sec / 10
        vx = v * math.cos(self.angle + math.pi/2) * self.scale
        vy = v * math.sin(self.angle + math.pi/2) * self.scale
        while True:
            if t < wait_sec:
                self.timer += 1
                self.x += vx
                self.y -= vy 
                self.putRoomba(self.timer, command=command)
            else:
                break
            t = round(t + 0.1, 1)


    def turn(self, rad_per_sec, wait_sec, command=""):
        # 0.1秒刻みで動くので、旋回スピードはrad_per_secの1/10となる
        t = 0
        a = rad_per_sec/10
        while True:
            if t < wait_sec:
                self.timer += 1
                self.angle += a
                self.putRoomba(self.timer, command=command)
            else:
                break
            t = round(t + 0.1, 1)

    def end(self):
        cv2.imshow(self.name, self.screen)
        if self.save_anim:
            self.save_anim_gif()
        cv2.waitKey(5000)
        cv2.destroyAllWindows()


    def save_anim_gif(self):
        imgPILS = [Image.fromarray(img[:, :, ::-1]) for img in self.imgs]           # 内包表記でPIL画像のリストを作る
        imgPILS[0].save("anim.gif", save_all=True, append_images=imgPILS[1:], 
            optimize=False, duration=100, loop=0)


    def scaling(self, list, scale=None):
        if scale is None:
            scale = self.scale
        np_arr = np.array(list)
        return  (np_arr * scale).astype(np.int16)

    def load_map(self, coursename):
        # csvを辞書として取り込む
        maze_data = {}
        with open("komono/" + coursename, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row):
                    for i, elm in enumerate(row):
                        elm = elm.strip()
                        sign = elm[0]
                        if sign == "-":
                            elm = elm[1:]
                        if elm.isnumeric():
                            row[i] = float(elm)
                            if sign == "-":
                                row[i] = -row[i]
                    key = row[0]
                    val = row[1:]
                    maze_data[key] = val

        # データに則って画像を描写する
        # 画像サイズ
        width, height = self.scaling(maze_data["size"], 1)
        imgH, imgW = self.scaling([height, width])
        map = np.full((imgH, imgW, 3), (255,255,255), np.uint8)


        # 原点
        x0, y0 = self.scaling(maze_data["origin"])
        
        # 枠
        x, y, w, h = self.scaling(maze_data["frame"])
        cv2.rectangle(map, (x0+x,y0+y), (x0+x+w, y0+y+h), (0,0,0), 4)

        # 方眼紙
        x1 = (x0/100 + 1) * 100
        x2 = ((width-x0)/100 + 1) * 100
        x1, x2, step = self.scaling(np.array([x0-x1, x0+x2, 100]))
        for x in range(x1, x2, step):
            cv2.line(map, (x,0), (x, height-1), (0,255,0), 1)

        y1 = (y0/100 + 1) * 100
        y2 = ((height-y0)/100 + 1) * 100
        y1, y2, step = self.scaling(np.array([y0-y1, y0+y2, 100]))
        for y in range(y1, y2, step):
            cv2.line(map, (0,y), (width-1, y), (0,255,0), 1)

        # スタート位置
        x, y, w, h = self.scaling(maze_data["start_area"])
        cv2.rectangle(map, (x0+x,y0-y), (x0+x+w, y0-y-h), (255,0,0), 2)

        # ゴール位置
        x, y, w, h = self.scaling(maze_data["goal_area"])
        cv2.rectangle(map, (x0+x,y0-y), (x0+x+w, y0-y-h), (255,0,0), 2)

        # ポール
        pts = self.scaling(maze_data["pole"])
        for i in range(0, len(pts), 2):
            x, y = pts[i], pts[i+1]
            cv2.circle(map, (x0+x,y0-y), int(150*self.scale), (255,0,0), -1)

        # ルンバスタート
        x, y = self.scaling(maze_data["start"])
        self.gx, self.gy = x0+x, y0-y

        # タイトル文字
        cv2.putText(map, self.name, (10, 40), self.font, 1.5, (0,0,255), 2)
        self.screen = map
        




def putSprite(back, front4, pos, angle=0, home=(0,0)):  # 角度はラジアン
    fh, fw = front4.shape[:2]
    bh, bw = back.shape[:2]
    x, y = pos
    xc, yc = home[0] - fw/2, home[1] - fh/2             # homeを左上基準から画像中央基準にする
    #a = np.radians(angle)
    rad = angle
    deg = rad / (2*math.pi/360)
    cos , sin = np.cos(rad), np.sin(rad)                # この三角関数は何度も出るので変数にする
    w_rot = int(fw * abs(cos) + fh * abs(sin))
    h_rot = int(fw * abs(sin) + fh * abs(cos))
    M = cv2.getRotationMatrix2D((fw/2,fh/2), deg, 1)    # 画像中央で回転
    M[0][2] += w_rot/2 - fw/2
    M[1][2] += h_rot/2 - fh/2
    imgRot = cv2.warpAffine(front4, M, (w_rot,h_rot))   # 回転画像を含む外接四角形

    # 外接四角形の全体が背景画像外なら何もしない
    xc_rot = xc * cos + yc * sin                        # 画像中央で回転した際の移動量
    yc_rot = -xc * sin + yc * cos
    x0 = int(x - xc_rot - w_rot / 2)                    # 外接四角形の左上座標   
    y0 = int(y - yc_rot - h_rot / 2)
    if not ((-w_rot < x0 < bw) and (-h_rot < y0 < bh)) :
        return back

    # 外接四角形のうち、背景画像内のみを取得する
    x1, y1 = max(x0,  0), max(y0,  0)
    x2, y2 = min(x0 + w_rot, bw), min(y0 + h_rot, bh)
    imgRot = imgRot[y1-y0:y2-y0, x1-x0:x2-x0]

    # マスク手法で外接四角形と背景を合成する
    result = back.copy()
    front = imgRot[:, :, :3]
    mask1 = imgRot[:, :, 3]
    mask = 255 - cv2.merge((mask1, mask1, mask1))
    roi = result[y1:y2, x1:x2]
    tmp = cv2.bitwise_and(roi, mask)
    tmp = cv2.bitwise_or(tmp, front)
    result[y1:y2, x1:x2] = tmp
    return result

if __name__ == "__main__":
    print("これ単品では動きません")
