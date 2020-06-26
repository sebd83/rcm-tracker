# -*- coding:utf-8 -*-
# PYTHON 3 code

# CelesTrak
# http://celestrak.com/NORAD/documentation/tle-fmt.php
# http://celestrak.com/columns/v04n03/#FAQ02
# https://celestrak.com/columns/v02n01/
# Data:
# http://celestrak.com/NORAD/elements/active.txt

from satellite_tracker import *
from datetime import timedelta, datetime, tzinfo, timezone
from dateutil import tz
from math import floor
import pytz
import matplotlib.pyplot as plt
from scipy.optimize import fmin, brentq

import sys

# Predicting next passes
# https://www.n2yo.com/passes/?s=44323

# TODO
# 1) complete Oblate Earth class --> DONE
# 2) convert functions to work with arrays of satellite positions (?)
# 3) add solver for predicting next passes
# 4) add sunrise and sunset predictions
# 5) complement solver for predicting next VISIBLE passes

def showCurrentPosition(rcm_sats, observer):
    # ====== Time of interest definition
    print("====== Live data")
    UTC_now = datetime.utcnow()
    print(UTC_now)
    JD_now = Julian.JD(UTC_now)
    GMST_now = Julian.GMST_JD(JD_now)


    # ====== Observer definition & Transformation of observer in ECI
    obs_Long = observer[0]
    obs_Lat = observer[1]
    obs_Alt = observer[2]
    xo,yo,zo = EarthSpherical.ECI_from_Long_Lat(GMST_now, obs_Long, obs_Lat, obs_Alt)

    for sat in rcm_sats:

        # ====== Propagation solving (from sgp4 lib)
        s, t = sat.NORAD_lines()
        print(sat.satellite_number)
        print(JD_now)
        satr = Satrec.twoline2rv(s, t)
        e, r, v = satr.sgp4(JD_now, 0) # TODO feedback the results to the tracked satellite ?

        print(f"Satellite: {sat.name}")
        #print(f"Error code: {e}")
        #print(f"Radial array: {r}")
        #print(f"Velocity arr: {v}")
        (xs, ys, zs) = (r[0], r[1], r[2])

        # ====== Transformation of SC ECI in Long/Lat
        scLong, scLat, scAlt = EarthOblate.Long_Lat_Alt_from_ECI(GMST_now, xs, ys, zs) # TODO make it work with vector ?
        #vLong, vLat, vAlt = EarthSpherical.Long_Lat_Alt_from_ECI(GMST_now, v[0], v[1], v[2], False) # TODO make it work with vector ?
        print(f"Longitude {scLong}")
        print(f"Latitude {scLat}")
        print(f"Altitude {scAlt}")
        #print(f"VLongitude {vLong}")
        #print(f"VLatitude {vLat}")
        #print(f"VAltitude {vAlt}")

        # testing reverse transformation
        #xt, yt, zt = EarthSpherical.ECI_from_Long_Lat(GMST_now, Lat, Long, Alt)
        #print(f"Radial #2 {xt}, {yt}, {zt}")

        # ====== Range vector & Transformation into TH CSYS
        (rx, ry, rz) = (xs - xo, ys - yo, zs - zo)
        az, el, rg = EarthSpherical.TH_from_ECI(GMST_now, obs_Long, obs_Lat, rx, ry, rz)
        print(f"Az/El/R: {az} , {el}, {rg}")


        #mv = MapVisualizer(sat, Long, Lat, vLong, vLat)
        #mv.plotBasemap()  

def plotNextHours(rcm_sat, nhoursdelta):
    start_time_UTC = UTC_now#datetime(2020, 6, 17, 7, 10, tzinfo=timezone.utc)
    end_time_UTC = start_time_UTC + timedelta(hours=nhoursdelta)#datetime(2020, 6, 17, 9, 45, tzinfo=timezone.utc)
    #start_time_UTC = UTC_now - timedelta(seconds=96.5*60)
    #end_time_UTC = UTC_now
    time_arr, el_arr = getElevationArray(rcm_sat, observer, start_time_UTC, end_time_UTC)
    plt.plot(time_arr, el_arr)
    plt.show()

def getElevationArray(rcm_sat, observer, start_time_UTC, end_time_UTC, step=60): #step in seconds
    
    print("====== Elevation PLOT ")
    #print(start_time_UTC)

    # ====== Time of interest ARRAY definition
    nsteps = floor((end_time_UTC - start_time_UTC)/timedelta(seconds=step))

    timearray = [start_time_UTC+timedelta(seconds=i*step) for i in range(nsteps)]
    JD_array = [Julian.JD_FR(ti) for ti in timearray]
    GMST_array = [Julian.GMST_JD_FR(jdi[0], jdi[1]) for jdi in JD_array]
    #print(timearray)
    #print(JD_array)
    #print(GMST_array)

    # ====== Observer definition ARRAY data & Transformation of observer in ECI
    obs_Long = observer[0]
    obs_Lat = observer[1]
    obs_Alt = observer[2]
    obs_coord_array = [EarthSpherical.ECI_from_Long_Lat(gmst_i, obs_Long, obs_Lat, obs_Alt) for gmst_i in GMST_array]
    #print(obs_coord_array[0:3])

    # ====== Propagation solving (from sgp4 lib)
    s, t = rcm_sat.NORAD_lines()
    satr = Satrec.twoline2rv(s, t)
    erv_array = [satr.sgp4(jdi[0], jdi[1]) for jdi in JD_array]
    #print(erv_array[0:3])

    # === Satellite position xyz
    xyz_sat_array = [(ervi[1][0], ervi[1][1], ervi[1][2]) for ervi in erv_array]
    #print(xyz_sat_array[0:3])

    xyz_rel_array = [(xyzs[0] - xyzo[0], xyzs[1] - xyzo[1], xyzs[2] - xyzo[2])
        for xyzs, xyzo in zip(xyz_sat_array, obs_coord_array)]
    #print(xyz_rel_array[0:3])

    az_el_rg_array = [EarthSpherical.TH_from_ECI(gmst_i, obs_Long, obs_Lat, xyzr[0], xyzr[1], xyzr[2]) 
        for gmst_i, xyzr in zip(GMST_array, xyz_rel_array)]
    #print(az_el_rg_array[0:3])

    el_array = [az_el_rg[1] for az_el_rg in az_el_rg_array]

    return timearray, el_array

def getTHData(JD_fr, JD_jd, rcm_sat, observer):

    # ====== Time of interest definition
    #jdi = Julian.JD_FR(time_UTC)
    gmst_i = Julian.GMST_JD_FR(JD_jd, JD_fr)

    # ====== Observer definition ARRAY data & Transformation of observer in ECI
    obs_Long = observer[0]
    obs_Lat = observer[1]
    obs_Alt = observer[2]
    xyzo = EarthSpherical.ECI_from_Long_Lat(gmst_i, obs_Long, obs_Lat, obs_Alt)

    # ====== Propagation solving (from sgp4 lib)
    s, t = rcm_sat.NORAD_lines()
    satr = Satrec.twoline2rv(s, t)
    ervi = satr.sgp4(JD_jd, JD_fr)

    # === Satellite position xyz
    xyzs = (ervi[1][0], ervi[1][1], ervi[1][2])
    #print(xyz_sat_array[0:3])
    xyzr = (xyzs[0] - xyzo[0], xyzs[1] - xyzo[1], xyzs[2] - xyzo[2])
    az, el, rg = EarthSpherical.TH_from_ECI(gmst_i, obs_Long, obs_Lat, xyzr[0], xyzr[1], xyzr[2])
    return (az, el, rg)

def getElevation(JD_fr, JD_jd, rcm_sat, observer):
    az, el, rg = getTHData(JD_fr, JD_jd, rcm_sat, observer)
    return el


def getNegElevation(JD_fr, JD_jd, rcm_sat, observer):
    return -getElevation(JD_fr, JD_jd, rcm_sat, observer)


def setObserverMontreal():
    obs_Lat = 45.5019327 # MONTREAL
    obs_Long = -73.6906396 # MONTREAL
    obs_Alt = 0.042 #42m

    return (obs_Long, obs_Lat, obs_Alt)

def findNextNRiseSetTimes(rcm_sat, observer, n, minElevation = 0):
    period = 96.5*60 #96.5 minutes
    golden = 1/1.6180339887
    
    time_a = UTC_now + timedelta(seconds=-period)
    jd_a, fr_a = Julian.JD_FR(time_a)
    #print(time_a)

    time_b = UTC_now
    jd_b, fr_b = Julian.JD_FR(time_b)
    #print(time_b)

    time_x = UTC_now + timedelta(seconds=-period*golden)
    jd_x, fr_x = Julian.JD_FR(time_x)
    #print(time_x)
    
    # --- First find the nearest min/max in the previous orbital period
    el_a = getElevation(fr_a, jd_a, rcm_sat, observer)
    el_b = getElevation(fr_b, jd_b, rcm_sat, observer)
    el_x = getElevation(fr_x, jd_x, rcm_sat, observer)

    xtol = 1.0/86400
    full_out = True
    disp = False
    min_max_found = None
    if el_x < el_a and el_x < el_b:
        # Search for minimum !
        xopt, fopt, iteri, fcalls, wflags = fmin(getElevation, fr_x, args=(jd_x, rcm_sat, observer), xtol=xtol, full_output=full_out, disp=disp)
        #print("\nMIN =")
        min_max_found = "min"
    elif el_x > el_a and el_x > el_b:
        # Search for maximum !
        xopt, fopt, iteri, fcalls, wflags = fmin(getNegElevation, fr_x, args=(jd_x, rcm_sat, observer), xtol=xtol, full_output=full_out, disp=disp)
        #print("\nMAX =")
        min_max_found = "max"
        fopt = -fopt
    else:
        # Pick the other golden value
        print("other golden value required")
        pass
    
    # Time xi is the local min/max
    time_xi = time_x + timedelta(seconds=(xopt[0]-fr_x)*86400)
    fopti = fopt
    #print(time_xi)
    jd_xi, fr_xi = Julian.JD_FR(time_xi)
    #print(getTHData(fr_xi, jd_xi, rcm_sat, observer))
    #print(f"Elevation= {fopt}")

    i = 0
    time_rise = None
    while i < n:
        # --- Second, define new timeline for search.
        # Time xii is the new guess looking forward 68% (golden ratio)
        time_xii = time_xi + timedelta(seconds=period*golden)
        jd_xii, fr_xii = Julian.JD_FR(time_xii)

        if min_max_found == "min":
            #Search for max now
            xopt, fopt, iteri, fcalls, wflags = fmin(getNegElevation, fr_xii, args=(jd_xii, rcm_sat, observer), xtol=xtol, full_output=full_out, disp=disp)
            #print("\nMAX =")
            min_max_found = "max"
            fopt = -fopt
        else:
            #Search for min now
            xopt, fopt, iteri, fcalls, wflags = fmin(getElevation, fr_xii, args=(jd_xii, rcm_sat, observer), xtol=xtol, full_output=full_out, disp=disp)
            #print("\nMIN =")
            min_max_found = "min"

        # Check if a root could be found between this new local min/max and the old one
        if fopti < 0 and fopt > 0 or fopti > 0 and fopt < 0:
            # Find root !
            rise_set = brentq(getElevation, fr_xi, xopt[0], args=(jd_xi, rcm_sat, observer), xtol=xtol, full_output=False, disp=disp)
            time_rise_set = time_xi + timedelta(seconds=(rise_set-fr_xi)*86400) 
            # If root is not in the past
            if time_rise_set > time_b:
                if fopti < 0 and fopt > 0:
                    #print("RISE = " + str(time_rise_set))
                    time_rise = time_rise_set
                else:
                    # yield the rise / set times + elevation at maximum (if greater than argument supplied)
                    #print("SET = " + str(time_rise_set))
                    time_set = time_rise_set
                    if fopti > minElevation:
                        yield [time_rise, time_set, fopti]
                        i += 1


        # Time xi is the local min/max
        time_xi = time_xii + timedelta(seconds=(xopt[0]-fr_xii)*86400)
        # Save this local min/max value
        fopti = fopt
        #print(time_xi)
        jd_xi, fr_xi = Julian.JD_FR(time_xi)
        #print(getTHData(fr_xi, jd_xi, sat1, observer))
        #print(f"Elevation= {fopt}")

def printRiseSetTimesMontreal(trise, tset, elevmax):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    trise = trise.replace(tzinfo=from_zone)
    trise = trise.astimezone(to_zone)
    tset = tset.replace(tzinfo=from_zone)
    tset = tset.astimezone(to_zone)
    print(f"Rise: {trise} / Set: {tset} / Elevation Max: {elevmax}")

if __name__ == '__main__':

    # ====== Declare satellites & get data
    ctrak = CelesTrak()
    ctrak.trackSatellite('RCM-1')
    ctrak.trackSatellite('RCM-2')
    ctrak.trackSatellite('RCM-3')
    ctrak.getData()

    UTC_now = datetime.utcnow()

    observer = setObserverMontreal()
    eastern = pytz.timezone('US/Eastern')

    # ====== Test 1 --> Show current RCM sats Position
    #showCurrentPosition(ctrak.listTrackedSats(), observer)

    # ====== Test 2 --> Plot the elevation for a RCM sat in the next 24 hours
    rcm1 = ctrak.getTrackedSat('RCM-1')
    rcm2 = ctrak.getTrackedSat('RCM-2')
    rcm3 = ctrak.getTrackedSat('RCM-3')
    #plotNextHours(rcm1, 9)

    # ===== Test 3 --> Find the next rise/set times by using a bisection method
    timesRCM1 = findNextNRiseSetTimes(rcm1, observer, 2, 30)
    timesRCM2 = findNextNRiseSetTimes(rcm2, observer, 2, 30)
    timesRCM3 = findNextNRiseSetTimes(rcm3, observer, 2, 30)

    print("RCM 1")
    t1r, t1s, elmax = next(timesRCM1)
    printRiseSetTimesMontreal(t1r, t1s, elmax)
    
    print("RCM 2")
    t2r, t2s, elmax = next(timesRCM2)
    printRiseSetTimesMontreal(t2r, t2s, elmax)

    print("RCM 3")
    t3r, t3s, elmax = next(timesRCM3)
    printRiseSetTimesMontreal(t3r, t3s, elmax)

    