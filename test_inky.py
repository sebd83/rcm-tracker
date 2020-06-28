# -*- coding:utf-8 -*-
# PYTHON 3 code

# Inky pHAT tutorial
# https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat
import PIL
from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT

#img = Image.new("RGB", (212,104))
img = Image.open("Inky/inky_test_yellow2.png")
print(img.palette)
draw = ImageDraw.Draw(img)

inky_display = InkyPHAT("yellow")
inky_display.set_border(inky_display.BLACK)

# Rise: 2020-06-25 06:18:06.230531-04:00 / Set: 2020-06-25 06:29:23.534293-04:00 / Elevation Max: 19.00227244173817
message = "↗ 06:18:06"
message2 = "⤒ 19.0°"
message3 = "↘ 06:29:23"
message4 = "testing 4th line"
message5 = "testing 5th line"
messageSAT = "RCM-2"

font = ImageFont.truetype("Verdana.ttf",14)
fontSAT = ImageFont.truetype("Verdana Bold.ttf",12)
w1, h1 = font.getsize(message)
w2, h2 = font.getsize(message2)
w3, h3 = font.getsize(message3)
w4, h4 = font.getsize(message4)
w5, h5 = font.getsize(message5)
wSAT, hSAT = fontSAT.getsize(messageSAT)

x1 = 212-10-w1
x2 = 212-10-w2
x3 = 212-10-w3#center:(212/2) - (w3/2)
x4 = 212-10-w4
x5 = 212-10-w5
xSAT = 20
ySAT = 104-hSAT-10

ys = (104-h1-h2-h3-h4-h5)/6
y1 = ys
y2 = 2*ys+h1
y3 = 3*ys+h1+h2
y4 = 4*ys+h1+h2+h3
y5 = 4*ys+h1+h2+h3+h4

draw.text((x1,y1), message, font=font, fill=2) #BLACK=0
draw.text((x2,y2), message2, font=font, fill=2) #WHITE=1
draw.text((x3,y3), message3, font=font, fill=2) #YELLOW=2
draw.text((x4,y4), message4, font=font, fill=2)
draw.text((x5,y5), message5, font=font, fill=2)
draw.text((xSAT,ySAT), messageSAT, font=fontSAT, fill=1)
#img.save('/Users/sebastien/Desktop/tst.png')
img.save('./tst.png')
inky_display.set_image(img)
inky_display.show()