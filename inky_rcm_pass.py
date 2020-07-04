# -*- coding:utf-8 -*-
# PYTHON 3 code

# Inky pHAT tutorial
# https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat
import PIL
from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
import os.path

#BUG: relative paths not working out of context

class Drawer:
    WIDTH  = 212
    HEIGHT = 104
    COLOR = "yellow"


class RCM_Drawer(Drawer):
    TEMPLATE_RELATIVE_PATH = "Inky/rcm_iso_left.png"
    MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
    TEMPLATE = os.path.join(MODULE_PATH, TEMPLATE_RELATIVE_PATH)
    MARGIN_TOP = 10
    MARGIN_RIGHT = 10
    MARGIN_BOTTOM = 10
    MARGIN_LEFT = 10
    SYMBOL_RISE = u"↗ "
    SYMBOL_SET_ = u"↘ "
    SYMBOL_ELEV = u"↑ "
    FONT_SIZE_LINES = 14
    FONT_SIZE_SAT   = 16
    FONT_FILE_SYMBL = os.path.join(MODULE_PATH, "Arial Unicode.ttf")
    FONT_FILE_LINES = os.path.join(MODULE_PATH, "Verdana Bold.ttf")
    FONT_FILE_SAT   = os.path.join(MODULE_PATH, "Verdana Bold.ttf")
    FONT_COLOR_LINES= 0 #WHITE
    FONT_COLOR_MIDDLE_LINE = 2#YELLOW
    FONT_COLOR_SAT  = 2 #YELLOW

    def __init__(self):
        #PIL images
        self.newImg_from_template()
        self.txt_lines = []
        self.txt_satellite = ""
        self.font_lines = ImageFont.truetype(self.FONT_FILE_LINES, self.FONT_SIZE_LINES)
        self.font_symbl = ImageFont.truetype(self.FONT_FILE_SYMBL, self.FONT_SIZE_LINES)
        self.font_sat   = ImageFont.truetype(self.FONT_FILE_SAT, self.FONT_SIZE_SAT)

    def newImg_from_template(self):
        self.img = Image.open(self.TEMPLATE)
        self.draw = ImageDraw.Draw(self.img)
        self.txt_lines = []
        self.txt_satellite = ""

    def set_image_Inky(self, save_img_path=None):
        inky_display = InkyPHAT(self.COLOR)
        inky_display.set_border(inky_display.BLACK)
        inky_display.set_image(self.img)
        inky_display.show()
        if save_img_path is not None:
            self.img.save(save_img_path)

    def set_pass_times_lines(self, rise_time_str, rise_az_str, set_time_str, set_az_str, elev_str):
        self.txt_lines.append(rise_time_str) #self.SYMBOL_RISE + 
        self.txt_lines.append(rise_az_str)
        self.txt_lines.append(elev_str) #self.SYMBOL_ELEV + 
        self.txt_lines.append(set_time_str) #self.SYMBOL_SET_ + 
        self.txt_lines.append(set_az_str)
        
        nlines = len(self.txt_lines)

        width_heights = [self.font_lines.getsize(txt_li) for txt_li in self.txt_lines]
        #Whitespace philosophy:
        #Full ws
        #Line1
        #Half ws
        #Line2
        #Full ws
        #Line3
        #Full ws
        #Line4
        #Half ws
        #Line 5
        #Full ws
        y_ws = (self.HEIGHT-sum([wh[1] for wh in width_heights]))/float(nlines)
        yi = 0
        li = 1
        for txt_li, wh in zip(self.txt_lines, width_heights):
            x = self.WIDTH - self.MARGIN_RIGHT - wh[0]
            if li in [1,3,4]:
                yi += y_ws # Add full whitespace before lines 1, 3, 4
            else:
                yi += y_ws/2 # Add half whitespace before lines 1, 3, 4
            y = int(yi)

            if li in [1,2,4,5]: # Adding an exception, color middle line in yellow (to distinguish)
                color_line = self.FONT_COLOR_LINES
            else:
                color_line = self.FONT_COLOR_MIDDLE_LINE
            
            self.draw.text((x,y), txt_li, font=self.font_lines, fill=color_line)

            #For lines 1, 3 and 4, add the relevant symbol
            if li == 1:
                x -= self.font_symbl.getsize(self.SYMBOL_RISE)[0] 
                self.draw.text((x,y), self.SYMBOL_RISE, font=self.font_symbl, fill=color_line)
            elif li == 3:
                x -= self.font_symbl.getsize(self.SYMBOL_ELEV)[0] 
                self.draw.text((x,y), self.SYMBOL_ELEV, font=self.font_symbl, fill=color_line)
            elif li == 4:
                x -= self.font_symbl.getsize(self.SYMBOL_SET_)[0] 
                self.draw.text((x,y), self.SYMBOL_SET_, font=self.font_symbl, fill=color_line)

            yi += wh[1]
            li += 1


    def set_satellite_name(self, sat_name):
        self.txt_satellite = str(sat_name)
        wSAT, hSAT = self.font_sat.getsize(self.txt_satellite)
        xSAT = self.MARGIN_LEFT
        ySAT = self.HEIGHT - hSAT - self.MARGIN_BOTTOM
        self.draw.text((xSAT,ySAT), self.txt_satellite, font=self.font_sat, fill=self.FONT_COLOR_SAT)

class WifiDrawer(Drawer):
    TEMPLATE_RELATIVE_PATH = "Inky/wifi_symbol.png"
    MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
    TEMPLATE = os.path.join(MODULE_PATH, TEMPLATE_RELATIVE_PATH)

    MARGIN_TOP = 10
    MARGIN_RIGHT = 10
    MARGIN_BOTTOM = 10
    MARGIN_LEFT = 90

    FONT_SIZE = 22
    FONT_FILE = os.path.join(MODULE_PATH, "Verdana Bold.ttf")
    FONT_COLOR= 2#YELLOW

    def __init__(self):
        #PIL images
        self.newImg_from_template()
        self.font = ImageFont.truetype(self.FONT_FILE, self.FONT_SIZE)
        self.WifiText = "No Wifi"
        self.set_Wifi_Line()


    def newImg_from_template(self):
        self.img = Image.open(self.TEMPLATE)
        self.draw = ImageDraw.Draw(self.img)

    def set_Wifi_Line(self):
        w, h = self.font.getsize(self.WifiText)
        x = self.MARGIN_LEFT
        y = self.HEIGHT - h - self.MARGIN_BOTTOM
        self.draw.text((x,y), self.WifiText, font=self.font, fill=self.FONT_COLOR)

    def set_image_Inky(self, save_img_path=None):
        inky_display = InkyPHAT(self.COLOR)
        inky_display.set_border(inky_display.BLACK)
        inky_display.set_image(self.img)
        inky_display.show()
        if save_img_path is not None:
            self.img.save(save_img_path)


if __name__ == '__main__':
    rcm_d = RCM_Drawer()

    sat_name  = "RCM#1"
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

    no_wifi = WifiDrawer()
    no_wifi.set_image_Inky()