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
from time import sleep
import sys

REFRESH_TIME = 15
SAVE_IMG_OUTPUT = './rcm_on_inky.png'

if __name__ == '__main__':
    # This module combines both the rcm_tracker logic and the inky_rcm_pass into
    # a global flow
    rcm_d = RCM_Drawer() #class to draw on inky
    observer, obs_timezone = setObserverMontreal()

    while True:

        #Get config file
        #TODO (with node-red)
        try:
            rcm1, rcm2, rcm3 = getAll3RCM()
        except ConnectError:
            no_wifi = WifiDrawer()
            no_wifi.set_image_Inky()
            sys.exit(0)

        timesRCM1 = findNextNRiseSetTimes(rcm1, observer, 1, 30)
        t1r, t1s, elmax, az1r, az1s = next(timesRCM1)
        d1r_str, t1r_str, az1r_str, d1s_str, t1s_str, az1s_str, elmax_str = printRiseSetTimes(obs_timezone, t1r, t1s, elmax, az1r, az1s)
        rcm_d.newImg_from_template()
        rcm_d.set_pass_times_lines(t1r_str, az1r_str, t1s_str, az1s_str, elmax_str)
        rcm_d.set_satellite_name("RCM-1")
        rcm_d.set_image_Inky(SAVE_IMG_OUTPUT)
        sleep(REFRESH_TIME)

        timesRCM2 = findNextNRiseSetTimes(rcm2, observer, 1, 30)
        t2r, t2s, elmax, az2r, az2s = next(timesRCM2)
        d2r_str, t2r_str, az2r_str, d2s_str, t2s_str, az2s_str, elmax_str = printRiseSetTimes(obs_timezone, t2r, t2s, elmax, az2r, az2s)
        rcm_d.newImg_from_template()
        rcm_d.set_pass_times_lines(t2r_str, az2r_str, t2s_str, az2s_str, elmax_str)
        rcm_d.set_satellite_name("RCM-2")
        rcm_d.set_image_Inky(SAVE_IMG_OUTPUT)
        sleep(REFRESH_TIME)

        timesRCM3 = findNextNRiseSetTimes(rcm3, observer, 1, 30)
        t3r, t3s, elmax, az3r, az3s = next(timesRCM3)
        d3r_str, t3r_str, az3r_str, d3s_str, t3s_str, az3s_str, elmax_str = printRiseSetTimes(obs_timezone, t3r, t3s, elmax, az3r, az3s)
        rcm_d.newImg_from_template()
        rcm_d.set_pass_times_lines(t3r_str, az3r_str, t3s_str, az3s_str, elmax_str)
        rcm_d.set_satellite_name("RCM-3")
        rcm_d.set_image_Inky(SAVE_IMG_OUTPUT)
        sleep(REFRESH_TIME)
