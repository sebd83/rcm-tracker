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
message = "Rise 06:18:06"
message2 = "Set 06:29:23"
message3 = "Elevation 19.0°"
messageSAT = "RCM-2"

font = ImageFont.truetype("Verdana.ttf",14)
fontSAT = ImageFont.truetype("Verdana Bold.ttf",12)
w1, h1 = font.getsize(message)
w2, h2 = font.getsize(message2)
w3, h3 = font.getsize(message3)
wSAT, hSAT = fontSAT.getsize(messageSAT)

x1 = 212-10-w1
x2 = 212-10-w2
x3 = 212-10-w3#center:(212/2) - (w3/2)
xSAT = 20
ySAT = 104-hSAT-10

print(h1)
print(h2)
print(h3)
ys = (104-h1-h2-h3)/4
y1 = ys
print(y1)
y2 = 2*ys+h1
print(y2)
y3 = 3*ys+h1+h2
print(y3)

draw.text((x1,y1), message, font=font, fill=2) #BLACK=0
draw.text((x2,y2), message2, font=font, fill=2) #WHITE=1
draw.text((x3,y3), message3, font=font, fill=2) #YELLOW=2
draw.text((xSAT,ySAT), messageSAT, font=fontSAT, fill=1)
#img.save('/Users/sebastien/Desktop/tst.png')
img.save('./tst.png')
inky_display.set_image(img)
inky_display.show()