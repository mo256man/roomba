from fileinput import filename
import cv2
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import glob

h0 = 100
w_size,h_size = 300, 200
wn, hn = 3, 2
names = [["テスト", "鳥居", "水野"],["板倉", "福田", "未設定"]]
font = "meiryob.ttc"
winname = "roomba menu"

def cv2_putText_5(img, text, org, fontFace, fontScale, color, mode=0):
# cv2.putText()にないオリジナル引数「mode」　orgで指定した座標の基準
# 0（デフォ）＝cv2.putText()と同じく左下　1＝左上　2＝中央

    # テキスト描写域を取得
    fontPIL = ImageFont.truetype(font = fontFace, size = fontScale)
    dummy_draw = ImageDraw.Draw(Image.new("RGB", (0,0)))
    text_w, text_h = dummy_draw.textsize(text, font=fontPIL)
    text_b = int(0.1 * text_h) # バグにより下にはみ出る分の対策

    # テキスト描写域の左上座標を取得（元画像の左上を原点とする）
    x, y = org
    offset_x = [0, 0, text_w//2]
    offset_y = [text_h, 0, (text_h+text_b)//2]
    x0 = x - offset_x[mode]
    y0 = y - offset_y[mode]
    img_h, img_w = img.shape[:2]

    # 画面外なら何もしない
    if not ((-text_w < x0 < img_w) and (-text_b-text_h < y0 < img_h)) :
        print ("out of bounds")
        return img

    # テキスト描写域の中で元画像がある領域の左上と右下（元画像の左上を原点とする）
    x1, y1 = max(x0, 0), max(y0, 0)
    x2, y2 = min(x0+text_w, img_w), min(y0+text_h+text_b, img_h)

    # テキスト描写域と同サイズの黒画像を作り、それの全部もしくは一部に元画像を貼る
    text_area = np.full((text_h+text_b,text_w,3), (0,0,0), dtype=np.uint8)
    text_area[y1-y0:y2-y0, x1-x0:x2-x0] = img[y1:y2, x1:x2]

    # それをPIL化し、フォントを指定してテキストを描写する（色変換なし）
    imgPIL = Image.fromarray(text_area)
    draw = ImageDraw.Draw(imgPIL)
    draw.text(xy = (0, 0), text = text, fill = color, font = fontPIL)

    # PIL画像をOpenCV画像に戻す（色変換なし）
    text_area = np.array(imgPIL, dtype = np.uint8)

    # 元画像の該当エリアを、文字が描写されたものに更新する
    img[y1:y2, x1:x2] = text_area[y1-y0:y2-y0, x1-x0:x2-x0]

    return img

def select_prog(event, x, y, flags, param):
    img = param["img"]
    if event == cv2.EVENT_LBUTTONDOWN:
        w = x//w_size
        h = (y-h0)//h_size
        name = ""
        if (0<=w<=wn) and (0<=h<=hn):
            name = names[h][w]
            print(h, w, name)
            dummy_draw = ImageDraw.Draw(Image.new("RGB", (0,0)))
            fontPIL = ImageFont.truetype(font = font, size = 80)
            tw, th = dummy_draw.textsize(name, fontPIL)
            img = cv2.rectangle(img, (int((w+0.5)*w_size)-tw//2-2, h0+int((h+0.5)*h_size)-th//2-2), (int((w+0.5)*w_size)+tw//2+2, h0+int((h+0.5)*h_size)+th//2+2), (255,255,255), -1)
            img = cv2_putText_5(img, names[h][w], (int((w+0.5)*w_size), h0+int((h+0.5)*h_size)), font, 90, (255,0,0), 2)
            cv2.imshow(winname, img)
            cv2.waitKey(100)

        cmd = "python "
        filename = "roomba_sim_amd_run_" + name + ".py"
        if glob.glob(filename):
            subprocess.run(cmd + filename)
        else:
            print("not found " + filename)

        fontPIL = ImageFont.truetype(font = font, size = 90)
        tw, th = dummy_draw.textsize(name, fontPIL)
        img = cv2.rectangle(img, (int((w+0.5)*w_size)-tw//2-2, h0+int((h+0.5)*h_size)-th//2-2), (int((w+0.5)*w_size)+tw//2+2, h0+int((h+0.5)*h_size)+th//2+2), (255,255,255), -1)
        img = cv2_putText_5(img, names[h][w], (int((w+0.5)*w_size), h0+int((h+0.5)*h_size)), font, 60, (0,0,255), 2)
        cv2.imshow(winname, img)

def main():
    img = np.full((h0+h_size*hn, w_size*wn,3), (255, 255, 255), dtype=np.uint8)
    img = cv2_putText_5(img, "Roomba Run Menu", (5,5), font, 80, (0,0,0), 1)
    for w in range(wn):
        for h in range(hn):
            cv2.rectangle(img, (w*w_size, h0+h*h_size), ((w+1)*w_size, h0+(h+1)*h_size), (0,0,0), 4)
            img = cv2_putText_5(img, names[h][w], (int((w+0.5)*w_size), h0+int((h+0.5)*h_size)), font, 60, (0,0,255), 2)

    cv2.imshow(winname, img)
    cv2.setMouseCallback(winname, select_prog, param={"img":img})
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
