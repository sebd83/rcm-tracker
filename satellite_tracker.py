# -*- coding:utf-8 -*-
# PYTHON 3 code

# CelesTrak
# http://celestrak.com/NORAD/documentation/tle-fmt.php
# http://celestrak.com/columns/v04n03/#FAQ02
# https://celestrak.com/columns/v02n01/
# Data:
# http://celestrak.com/NORAD/elements/active.txt

import requests
from math import sin, cos, asin, atan, atan2, pi, modf, radians, degrees, sqrt
from datetime import datetime
from python_sgp4_master.sgp4.api import Satrec
# To draw maps
#from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import sys

# Predicting next passes
# https://www.n2yo.com/passes/?s=44323

# TODO
# 1) complete Oblate Earth class --> DONE
# 2) convert functions to work with arrays of satellite positions (?)
# 3) add solver for predicting next passes
# 4) add sunrise and sunset predictions
# 5) complement solver for predicting next VISIBLE passes

class Julian:
    """
    This class contains simple functions to compute julian days.
    http://celestrak.com/columns/v02n02/

    Tested with Jan 1st 00:00 of 1599, 1600, 1601, 1999, 2000, 2001, 2019
    and with Oct 1st 1995 00:00
    and with Oct 1st 1995 09:00 UTC
    """
    @staticmethod
    def JDoY(year):
        """ Calculate Julian Date of 0.0 Jan year """
        year -= 1
        A = int(year/100)
        B = 2 - A + int(A/4)
        return int(365.25*year) + int(30.6001*14) + + 1720994.5 + B

    @staticmethod
    def DoY(yr, mo, dy):
        """ """
        days = [31,28,31,30,31,30,31,31,30,31,30,31]
        day = 0
        for i in range(mo-1):
            day += days[i]
        day += dy
        if ((yr % 4) == 0) and (((yr % 100) != 0) or ((yr % 400) == 0)) and (mo > 2):
            day += 1
        return day

    @classmethod
    def JD(cls, dt): # was JD(cls, yr, mo, dy, hr, mm, sc):
        """ combining JDoY and DoY and adding hours/min/sec (in julian time -> 24h a day)"""
        # Nomenclature ==> dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
        return cls.JDoY(dt.year) + cls.DoY(dt.year,dt.month,dt.day) + dt.hour/24.0 + dt.minute/(1440.0) + dt.second/86400.0

    @classmethod
    def JD_FR(cls, dt):
        """ Returns the Julian Day along with fraction for better accuracy"""
        return (cls.JDoY(dt.year) + cls.DoY(dt.year,dt.month,dt.day), dt.hour/24.0 + dt.minute/(1440.0) + dt.second/86400.0)

    @staticmethod
    def GMST_JD(jd:float)->float:
        """
        Function ThetaG_JD(jd : double) : double;
        { Reference:  The 1992 Astronomical Almanac, page B6. }
          var
            UT,TU,GMST : double;
          begin
          UT   := Frac(jd + 0.5);
          jd   := jd - UT;
          TU   := (jd - 2451545.0)/36525;
          GMST := 24110.54841 + TU * (8640184.812866 + TU * (0.093104 - TU * 6.2E-6));
          GMST := Modulus(GMST + 86400.0*1.00273790934*UT,86400.0);
          ThetaG_JD := twopi * GMST/86400.0;
          end; {Function ThetaG_JD}
          """
        UT, UTint = modf(jd+0.5)
        jd = jd - UT
        TU = (jd - 2451545.0)/36525
        GMST = 24110.54841 + TU * (8640184.812866 + TU * (0.093104 - TU * 6.2E-6))
        GMST = (GMST + 86400.0*1.00273790934*UT) % 86400
        return pi*2 * GMST/86400.0

    @classmethod
    def GMST(cls, dt)->float:
        return cls.GMST_JD(cls.JD(dt))

    @classmethod
    def GMST_JD_FR(cls, jd, fr)->float:
        return cls.GMST_JD(jd+fr)

class EarthSpherical:
    """ """
    Re = 6378.135 #km

    @classmethod
    def TH_from_ECI(cls, GMST, Long, Lat, rx, ry, rz):
        """
        Transforms the range vector (from observer to satellite)
        from the ECI CSYS
        to the Topocentric-Horizon CSYS

        top_s := Sin(lat)* Cos(theta)*rx
                 + Sin(lat)* Sin(theta)*ry
                 - Cos(lat)*rz
          top_e := - Sin(theta)*rx
                 + Cos(theta)*ry;
          top_z := Cos(lat)* Cos(theta)*rx
                 + Cos(lat)* Sin(theta)*ry
                 + Sin(lat)*rz;
          az := ArcTan(-top_e/top_s);
          if top_s > 0 then
            az := az + pi;
          if az < 0 then
            az := az + twopi;
          rg := Sqrt(rx*rx + ry*ry + rz*rz);
          el := ArcSin(top_z/rg);
          end; {Procedure Calculate_Look}
        """
        phi = radians(Lat)
        #phi = radians(90-Lat) # SD
        #print(f"phi: {phi}")
        lambda_e = radians(Long)
        theta = GMST + lambda_e #theta_g + lambda_e

        #range_ = sqrt(rx*rx + ry*ry + rz*rz)
        #print(range_)
        rsouth =  sin(phi)*cos(theta)*rx + sin(phi)*sin(theta)*ry - cos(phi)*rz
        reast  = -sin(theta)*rx + cos(theta)*ry
        rzenith = cos(phi)*cos(theta)*rx + cos(phi)*sin(theta)*ry + sin(phi)*rz
        #range_ = sqrt(rsouth**2 + reast**2 + rzenith**2)
        #print(range_)
        #rsouth = cos(phi)*cos(theta)*rx - cos(phi)*sin(theta)*ry + sin(phi)*rz
        #reast  = sin(theta)*rx + cos(theta)*ry
        #rzenith = -sin(phi)*cos(theta)*rx + sin(phi)*sin(theta)*ry + cos(phi)*rz
        #range_ = sqrt(rsouth**2 + reast**2 + rzenith**2)
        #print(range_)

        azimuth = atan(-reast/rsouth)
        if rsouth > 0:
            azimuth += pi
        if azimuth < 0:
            azimuth += 2*pi
        range_ = sqrt(rx*rx + ry*ry + rz*rz)
        #print(f"rx: {rx}   /   ry: {ry}   /   rz: {rz}")
        #print(f"rs: {rsouth}   /   re: {reast}")
        #print(f"rz: {rzenith}   /   range: {range_}")
        elevat = asin(rzenith/range_)
        # Convert to degrees and return values
        return (degrees(azimuth), degrees(elevat), range_)


    @classmethod
    def ECI_from_Long_Lat(cls, GMST, Long, Lat, altitude=0):
        """
        Calculates the ECI coordinates x, y, z from a long, lat at a given GMST time
        GMST in rad
        Lat in deg
        Long in deg
        Lat = phi, Long = lambda_e -> theta (from GMST)

        """
        phi = radians(Lat)
        lambda_e = radians(Long)
        theta = GMST + lambda_e #theta_g + lambda_e

        R = cls.Re + altitude
        z = R*sin(phi)
        x = R*cos(phi)*cos(theta)
        y = R*cos(phi)*sin(theta)

        return (x,y,z)

    # OLD method
    # @classmethod
    # def Long_Lat_Alt_from_ECI(cls, GMST, x, y, z, add_Re=True):
    #     """
    #     Calculates the Longitude, Latitude and Altitude from coordinates x, y, z at a given GMST time
    #     GMST in rad
    #     x, y, z in km
    #     """
        
    #     # Calculate theta from -pi to +pi
    #     # Calculate Longitude from -180deg to 180deg
    #     theta = atan2(y,x)
    #     lambda_e = theta - GMST
    #     Long = degrees(lambda_e)
    #     Long = (Long + 180) % 360 - 180

    #     # Calculate phi from -pi/2 to +pi/2
    #     if abs(x) > 1:
    #         phi = atan(z*cos(theta)/x) # x must not be 0 
    #     elif abs(y) > 1:
    #         phi = atan(z*sin(theta)/y) # y must not be 0
    #     else:
    #         print(f"|x| and |y| < 1: {x} {y}")
    #         raise ZeroDivisionError("x and y are both too small")

    #     Lat = degrees(phi)

    #     # Calculate altitude
    #     if abs(degrees(phi))<30: # near equator, sin(phi) nears 0, use cos
    #         if abs(degrees(theta))<30: #near greenwich for GMST (close to 0), use cos
    #             R = x/cos(phi)/cos(theta)
    #         else:
    #             R = y/cos(phi)/sin(theta)
    #     else:
    #         R = z/sin(phi)
        
    #     if add_Re:
    #         Alt = R - cls.Re
    #     else:
    #         Alt = R

    #     return (Long, Lat, Alt)


    @classmethod
    def Long_Lat_Alt_from_ECI(cls, GMST, x, y, z, add_Re=True):
        """
        Calculates the Longitude, Latitude and Altitude from coordinates x, y, z at a given GMST time
        GMST in rad
        x, y, z in km
        """
        
        # Calculate theta from -pi to +pi
        # Calculate Longitude from -180deg to 180deg
        theta = atan2(y,x)
        lambda_e = theta - GMST
        Long = degrees(lambda_e)
        Long = (Long + 180) % 360 - 180

        # Calculate phi from -pi/2 to +pi/2
        phi = atan(z/sqrt(x*x + y*y))
        Lat = degrees(phi)

        Alt = sqrt(x*x + y*y + z*z) - cls.Re

        return (Long, Lat, Alt)


class EarthOblate:
    """ """
    Ra = 6378.135 #km
    f = 1/298.26
    Rb = Ra*(1-f)

    @classmethod
    def TH_from_ECI(cls, GMST, Long, Lat, rx, ry, rz):
        pass

    @classmethod
    def ECI_from_Long_Lat(cls, GMST, Long, Lat, altitude=0):
        """
        Calculates the ECI coordinates x, y, z from a long, lat at a given GMST time
        GMST in rad
        Lat in deg
        Long in deg
        Lat = phi, Long = lambda_e -> theta (from GMST)
        """

        phi = radians(Lat)
        lambda_e = radians(Long)
        theta = GMST + lambda_e #theta_g + lambda_e

        C = 1/sqrt(1+cls.f*(cls.f-2)*sin(phi)**2)
        S = (1-cls.f)**2*C

        ## WORKS NOW add altitude to earth ellipse radius
        R = cls.Ra
        x = (R * C + altitude) * cos(phi)*cos(theta)
        y = (R * C + altitude) * cos(phi)*sin(theta)
        z = (R * S + altitude) * sin(phi)

        return (x,y,z)

    @classmethod
    def Long_Lat_Alt_from_ECI(cls, GMST, x, y, z, add_Re=True):
        # Celestrak column "Orbital Coordinate Systems, Part III"
        """
        Calculates the Longitude, Latitude and Altitude from coordinates x, y, z at a given GMST time
        GMST in rad
        x, y, z in km
        """

        # Calculate theta from -pi to +pi
        # Calculate Longitude from -180deg to 180deg
        theta = atan2(y,x)
        lambda_e = theta - GMST
        Long = degrees(lambda_e)
        Long = (Long + 180) % 360 - 180

        # Calculate phi with iterations
        R = sqrt(x*x + y*y)
        #First approximation --> Same as spherical earth
        phi = atan(z/sqrt(x*x + y*y))
        e2 = 2*cls.f-cls.f**2
        error = 9

        while error > 1e-8:
            phii = phi # Get phi from last iteration
            C = 1/sqrt(1- e2 * sin(phii)**2)
            phi = atan((z + cls.Ra*C*e2 *sin(phii))/R)
            error = phi - phii

        Lat = degrees(phi)
        Alt = R / cos(phi) - cls.Ra*C
        return (Long, Lat, Alt)



class CelesTrak:
    """
    This class contains the logic to download 2-line elements from
    Celestrak website (source=NORAD)
    Nomenclature = http://celestrak.com/NORAD/documentation/tle-fmt.php
    """

    def __init__(self):
        self.data_url = "http://celestrak.com/NORAD/elements/active.txt"
        self.tracked = dict()

    def trackSatellite(self, name):
        # Add satellite to the list of tracked satellites
        # (for parsing all at once)
        if name not in self.tracked:
            self.tracked[name] = Satellite(name)

    def listTrackedSats(self):
        for sat in self.tracked.values():
            print(sat.name)
            yield sat

    def getTrackedSat(self, name):
        for sat in self.tracked.values():
            if sat.name == name:
                return sat

    def _loadDataPage(self):
        # Internal method used by getData -> HTML doc request
        self.data_request = requests.get(self.data_url)
        self.data_doc = self.data_request.text

    def getData(self):
        # Gets the 2-line element data for each satellite tracked
        # Only works with 1+ satellites in self.tracked
        nparsed = 0
        if self.tracked: # if dict is not empty
            self._loadDataPage()

            data_doc_iterable = iter(self.data_doc.splitlines())
            
            for line in data_doc_iterable: # Loop lines of HTML doc
                for satname, sat in self.tracked.items(): # Check if line is one of the sats

                    if satname == line.strip(): # name must correspond to the line exactly
                        nparsed += 1
                        two_line1 = next(data_doc_iterable)
                        two_line2 = next(data_doc_iterable)
                        sat.parseNORAD(two_line1, two_line2)

        return nparsed
            

class Satellite:
    """  """

    def __init__(self, name):
        self.name = name

        self.satellite_number = None
        self.classification = None
        self.launch_year = None
        self.launch_number = None
        self.launch_piece = None
        self.epoch_year = None
        self.epoch_day = None
        self.first_derivative = None
        self.second_derivative = None
        self.bstar_drag = None
        self.ephemeris_type = None
        self.element_number = None
        self.checksum1 = None
        self.NORAD_line1 = None
        
        self.inclination = None
        self.right_asc = None
        self.eccentricity = None
        self.arg_perigee = None
        self.mean_anomaly = None
        self.mean_notion = None
        self.revolution_number = None
        self.checksum2 = None
        self.NORAD_line2 = None

    def parseNORAD(self, norad_line1, norad_line2):
        
        self.NORAD_line1 = norad_line1
        self.satellite_number = norad_line1[2:7]
        self.classification = norad_line1[7]
        self.launch_year = norad_line1[9:11]
        self.launch_number = norad_line1[11:14] #Convention uses leading zeros for fields 1.5 and 1.8 and leading spaces elsewhere, but either is valid.
        self.launch_piece = norad_line1[14:17]
        self.epoch_year = int(norad_line1[18:20])
        self.epoch_day = float(norad_line1[20:32]) #Convention uses leading zeros for fields 1.5 and 1.8 and leading spaces elsewhere, but either is valid.
        self.first_derivative = float(norad_line1[33:43]) ## The first six columns of each field represent the mantissa and the last two represent the exponent. 
        self.second_derivative = float(norad_line1[44] + '.' + norad_line1[45:50]) # For example, the value -12345-6 corresponds to -0.12345 × 10-6. Each of these two fields can be blank, corresponding to a value of zero.
        self.second_derivative = self.second_derivative * pow(10.0, int(norad_line1[50:52]))
        self.bstar_drag = float(norad_line1[53] + '.' + norad_line1[54:59])
        self.bstar_drag = self.bstar_drag * pow(10.0, int(norad_line1[59:61]))
        self.ephemeris_type = norad_line1[62]
        self.element_number = int(norad_line1[64:68])
        self.checksum1 = norad_line1[68]
        # checksum verification

        self.NORAD_line2 = norad_line2
        self.inclination = float(norad_line2[8:16])   #Fields 2.3 --> units of degrees and can range from 0 up to 180 degrees
        self.right_asc = float(norad_line2[17:25])    #Fields 2.4 --> units of degrees and can range from 0 up to 360 degrees
        self.eccentricity = float('0.' + norad_line2[26:33].strip()) #The eccentricity (field 2.5) is a unitless value with an assumed leading decimal point.
        self.arg_perigee = float(norad_line2[34:42])  #Fields 2.6 --> units of degrees and can range from 0 up to 360 degrees
        self.mean_anomaly = float(norad_line2[43:51]) #Fields 2.7 --> units of degrees and can range from 0 up to 360 degrees
        self.mean_notion = float(norad_line2[52:63])  #The mean motion (field 2.8) is measured in revolutions per day
        self.revolution_number = norad_line2[63:68]
        self.checksum2 = norad_line2[68]
        # checksum verification

    def NORAD_lines(self):
        return (self.NORAD_line1, self.NORAD_line2)

    def __str__(self):
        return f"{self.name}\n{self.NORAD_line1}\n{self.NORAD_line2}"
    def __repr__(self):
        i = "0123456789x123456789xx23456789xxx3456789xl23456789l123456789lx2345678"
        return f"{self.name}\n{self.NORAD_line1}\n{i}\n{self.NORAD_line2}\n{i}"

class MapVisualizer:

    def __init__(self, sat, Long, Lat, vLong = 1, vLat = 1):
        self.sat = sat
        self.Long = Long
        self.Lat = Lat
        self.vLong = vLong
        self.vLat = vLat


    # def plotBasemap(self):
    #     # set up orthographic map projection with
    #     # perspective of satellite looking down at 50N, 100W.
    #     # use low resolution coastlines.
    #     map = Basemap(projection='ortho',lat_0=self.Lat,lon_0=self.Long,resolution='l')
    #     # draw coastlines, country boundaries, fill continents.
    #     map.drawcoastlines(linewidth=0.25)
    #     map.drawcountries(linewidth=0.25)
    #     map.fillcontinents(color='green',lake_color='aqua')
    #     # draw the edge of the map projection region (the projection limb)
    #     map.drawmapboundary(fill_color='aqua')
    #     # draw lat/lon grid lines every 30 degrees.
    #     map.drawmeridians(np.arange(0,360,30))
    #     map.drawparallels(np.arange(-90,90,30))
    #     # make up some data on a regular lat/lon grid.
    #     x = np.array([self.Long])
    #     y = np.array([self.Lat])
    #     u = np.array([self.vLong])
    #     v = np.array([self.vLat])
    #     # rotate the speed vectors in the map coordinates
    #     u_map, v_map, x_map, y_map = map.rotate_vector(u, v, x, y, returnxy=True)
    #     plott = map.plot(x_map, y_map, marker='D',color='m')
    #     #quiv = map.quiver(x_map, y_map, u_map, v_map, latlon=False, linewidths=1.5, scale=1)
    #     # compute native map projection coordinates of lat/lon grid.
    #     #x, y = map(lons*180./np.pi, lats*180./np.pi)
    #     # contour data over the map.
    #     #cs = map.contour(x,y,wave+mean,15,linewidths=1.5)
    #     plt.title('RCM spacecraft now')
    #     plt.show()


if __name__ == '__main__':

    # ====== Declare satellites & get data
    ctrak = CelesTrak()
    ctrak.trackSatellite('RCM-1')
    ctrak.trackSatellite('RCM-2')
    ctrak.trackSatellite('RCM-3')
    ctrak.getData()

    # ====== Test data for dates conversion
    # print("Test from Celestrak")
    # GMST_oct_1_1995 = Julian.GMST_JD(Julian.JD(datetime(1995,10,1,9,0,0)))
    # print(GMST_oct_1_1995)
    # x,y,z = EarthOblate.ECI_from_Long_Lat(GMST_oct_1_1995, -75, 40, 0.042)
    # x,y,z = EarthSpherical.ECI_from_Long_Lat(GMST_oct_1_1995, -75, 40, 0.042)
    # print(x)
    # print(y)
    # print(z)
    # #=WORKS test the conversion back
    # Long, Lat, Alt = EarthOblate.Long_Lat_Alt_from_ECI(GMST_oct_1_1995, x, y, z)
    # Long, Lat, Alt = EarthSpherical.Long_Lat_Alt_from_ECI(GMST_oct_1_1995, x, y, z)
    # print(Long)
    # print(Lat)
    # print(Alt)

    # ====== Test data for MIR station from v02n03
    

    # ====== Time of interest definition
    print("====== Live data")
    UTC_now = datetime.utcnow()
    print(UTC_now)
    GMST_now = Julian.GMST(UTC_now)

    # ====== Observer definition & Transformation of observer in ECI
    #obs_Lat = 89    
    obs_Lat = 45.5019327 # MONTREAL
    obs_Long = -73.6906396 # MONTREAL
    obs_Alt = 0.042 #42m
    xo,yo,zo = EarthSpherical.ECI_from_Long_Lat(GMST_now, obs_Long, obs_Lat, obs_Alt)
