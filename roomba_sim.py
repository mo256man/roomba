import cv2
import numpy as np
from simulator import *
import math

sim = Roomba_sim()

cm_sec = 20      # cm_sec
wait_time = 10  # sec

a = 60
wait_sec = 5
angle = 2*math.pi/360 * a
rad_per_sec = angle / wait_sec

sim.stop()
sim.turn(-0.5*rad_per_sec, wait_sec)
sim.go(100, 5)
sim.turn(2*rad_per_sec, wait_sec)
sim.go(100, 5)
sim.turn(2*rad_per_sec, wait_sec)
sim.go(100, 5)
sim.turn(2.5*rad_per_sec, wait_sec)

sim.save_anim_gif()

cv2.waitKey(1000)
cv2.destroyAllWindows()
