# -*- coding:utf-8 -*-
# PYTHON 3 code
#
#         +--------------+
#         | RASP.PI BOOT |
#         +-------+------+
#                 |
#                 |
#                 |
#         +-------v-------+
#         | Loop Infinite <----------------------+
#         +-------+-------+                      |
#                 |                              |
#                 |                              |
#                 |                              |
#        +--------v---------+                    |
#        | Get config file: |                    |
#        | node-red switch  |                    |
#        | -weather or RCM  |                    |
#        +--------+---------+                    |
#                 |                              |
#                 +-------------+                |
#                 |             |                |
# +---------------v+     +------v---------+      |
# | Weather:       |     | RCM            |      |
# | Update display |     | Update display |      |
# | 1. NOW         |     | 1. RCM-1       |      |
# | sleep (10)     |     | sleep (10)     |      |
# | 2. 36h         |     | 2. RCM-2       |      |
# | sleep (10)     |     | sleep (10)     |      |
# | 3. 3 days      |     | 3. RCM-3       |      |
# | sleep (10)     |     | sleep (10)     |      |
# +--------------+-+     +--------------+-+      |
#                |                      |        |
#                |                      +--------+
#                +-------------------------------+
from rcm_tracker import *
from inky_rcm_pass import *

REFRESH_TIME = 15
SAVE_IMG_OUTPUT = './rcm_on_inky.png'

if __name__ == '__main__':
    # This module combines both the rcm_tracker logic and the inky_rcm_pass into
    # a global flow
    rcm_d = RCM_Drawer() #class to draw on inky

    while True:

        #Get config file
        #TODO (with node-red)

        rcm1, rcm2, rcm3 = getAll3RCM()
        timesRCM1 = findNextNRiseSetTimes(rcm1, observer, 1, 30)
        t1r, t1s, elmax, az1r, az1s = next(timesRCM2)
        rcm_d.newImg_from_template()
        rcm_d.set_pass_times_lines(t1r, az1r, t1s, az1s, elmax)
        rcm_d.set_satellite_name("RCM-1")
        rcm_d.set_image_Inky(SAVE_IMG_OUTPUT)
        sleep(REFRESH_TIME)

        timesRCM2 = findNextNRiseSetTimes(rcm2, observer, 1, 30)
        t2r, t2s, elmax, az2r, az2s = next(timesRCM2)
        rcm_d.newImg_from_template()
        rcm_d.set_pass_times_lines(t2r, az2r, t2s, az2s, elmax)
        rcm_d.set_satellite_name("RCM-2")
        rcm_d.set_image_Inky(SAVE_IMG_OUTPUT)
        sleep(REFRESH_TIME)

        timesRCM3 = findNextNRiseSetTimes(rcm3, observer, 1, 30)
        t3r, t3s, elmax, az3r, az3s = next(timesRCM3)
        rcm_d.newImg_from_template()
        rcm_d.set_pass_times_lines(t3r, az3r, t3s, az3s, elmax)
        rcm_d.set_satellite_name("RCM-3")
        rcm_d.set_image_Inky(SAVE_IMG_OUTPUT)
        sleep(REFRESH_TIME)