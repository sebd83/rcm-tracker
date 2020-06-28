# -*- coding:utf-8 -*-
# PYTHON 3 code

# Inky pHAT tutorial
# https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat
import PIL
from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT

class RCM_Drawer:
    TEMPLATE = "Inky/rcm_iso_left.png"
    WIDTH  = 212
    MARGIN_TOP = 10
    MARGIN_RIGHT = 10
    MARGIN_BOTTOM = 10
    MARGIN_LEFT = 10
    HEIGHT = 104
    COLOR = "yellow"
    SYMBOL_RISE = u"↗"
    SYMBOL_SET_ = u"↘"
    SYMBOL_ELEV = u"↑"
    FONT_SIZE_LINES = 12
    FONT_SIZE_SAT   = 16
    FONT_FILE_LINES = "Arial Unicode.ttf"
    FONT_FILE_SAT   = "Verdana Bold.ttf"
    FONT_COLOR_LINES= 0 #WHITE
    FONT_COLOR_SAT  = 2 #YELLOW

    def __init__(self):
        #PIL images
        self.newImg_from_template()
        self.txt_lines = []
        self.txt_satellite = ""
        self.font_lines = ImageFont.truetype(self.FONT_FILE_LINES, self.FONT_SIZE_LINES)
        self.font_sat   = ImageFont.truetype(self.FONT_FILE_SAT, self.FONT_SIZE_SAT)

    def newImg_from_template(self):
        self.img = Image.open(self.TEMPLATE)
        self.draw = ImageDraw.Draw(self.img)

    def set_image_Inky(self, save_img_path=None):
        inky_display = InkyPHAT(self.COLOR)
        inky_display.set_border(inky_display.BLACK)
        inky_display.set_image(self.img)
        inky_display.show()
        if save_img_path is not None:
            self.img.save(save_img_path)

    def set_pass_times_lines(self, rise_time_str, rise_az, set_time_str, set_az, elev):
        self.txt_lines.append(self.SYMBOL_RISE + str(rise_time_str))
        self.txt_lines.append(str(rise_az))
        self.txt_lines.append(self.SYMBOL_ELEV + str(elev))
        self.txt_lines.append(str(set_az))
        self.txt_lines.append(self.SYMBOL_SET_ + str(set_time_str))
        nlines = len(self.txt_lines)

        width_heights = [self.font_lines.getsize(txt_li) for txt_li in self.txt_lines]
        y_ws = (self.HEIGHT-sum([wh[1] for wh in width_heights]))/(nlines+1.0)
        print([wh[1] for wh in width_heights])
        print(y_ws)
        yi = 0
        for txt_li, wh in zip(self.txt_lines, width_heights):
            x = self.WIDTH - self.MARGIN_RIGHT - wh[0]
            yi += y_ws
            y = int(yi)
            print(y)
            self.draw.text((x,y), txt_li, font=self.font_lines, fill=self.FONT_COLOR_LINES)
            yi += wh[1]

    def set_satellite_name(self, sat_name):
        self.txt_satellite = str(sat_name)
        wSAT, hSAT = self.font_sat.getsize(self.txt_satellite)
        xSAT = self.MARGIN_LEFT
        ySAT = self.HEIGHT - hSAT - self.MARGIN_BOTTOM
        self.draw.text((xSAT,ySAT), self.txt_satellite, font=self.font_sat, fill=self.FONT_COLOR_SAT)

if __name__ == '__main__':
    rcm_d = RCM_Drawer()

    sat_name = "RCM-1"
    rise_time = "06:41:44"
    rise_az   = "21 NNE"
    set_time  = "06:53:51"
    set_az    = "172 S"
    elev      = "33.1°"
    #RCM 1
    #R: 06:41:44 @NNE21 / S: 06:53:51 @S172/ El. Max: 33.1
    rcm_d.set_pass_times_lines(rise_time, rise_az, set_time, set_az, elev)
    rcm_d.set_satellite_name(sat_name)

    save_output = './rcm_on_inky.png'
    rcm_d.set_image_Inky(save_output)