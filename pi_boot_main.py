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