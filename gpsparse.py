import re
from datetime import datetime

# We want to store the GPS annotations in decimal degrees (DD) but the GPS file
# provides the information in Degree, Minute, Seconds (DMS).  These helper functions 
# perform conversion for us.
def lon_to_decimal(deg,minute,sec,dir):
    val = deg + minute/60 + sec/3600
    if dir == 'W':
        val = -val
    return val

def lat_to_decimal(deg,minute,sec,dir):
    val = deg + minute/60 + sec/3600
    if dir == 'S':
        val = -val
    return val

# Define regular expressions to assist us in parsing the GPS file
# Regex to match lines with timestamp information
prog_ts = re.compile('\[(\d+-\d+-\d+)\s+-\s+(\d+:\d+:\d+)')
# Regex to match lines with latitude and longitude information
prog_lat_lon = re.compile('^\s*(.+)\xa1\xe3(.+)\'(.+)" ([EWSN])')
# Regex to match lines containing speed information
prog_speed = re.compile('Speed:\s*(\S+)\s*KPH')

def parseLonLine(line):
    lon_res = prog_lat_lon.match(line)
    lon = lon_res.groups()
    lon_dd = lon_to_decimal(float(lon[0]),float(lon[1]),float(lon[2]),lon[3])
    return lon_dd

def parseLatLine(line):
    lat_res = prog_lat_lon.match(line)
    lat = lat_res.groups()
    lat_dd = lat_to_decimal(float(lat[0]),float(lat[1]),float(lat[2]),lat[3])
    return lat_dd

# Helper function to convert line of text from the file into a date object.
def getDateObjectForLine(line):
    # Test that the current line looks like a timestamp
    is_time_stamp = prog_ts.match(line)
    if is_time_stamp is None:
        return None
    else:
        date,time = is_time_stamp.groups()  
        dtstr = "{} {}".format(date,time)
        return datetime.strptime(dtstr, '%Y-%m-%d %H:%M:%S')

# Helper class to track the timedelta between GPS readings.  We use to 
# preserve the time delta between GPS readings when the user specifies
# a custom start timestamp.
class TimeStepTracker(object):    
    def __init__(self):
        self.previous_datetime_object = None
    
    def getTimeDelta(self,next_date):
        if self.previous_datetime_object is None:
            self.previous_datetime_object = next_date
            return next_date - next_date
        else:
            timedelta = next_date - self.previous_datetime_object
            self.previous_datetime_object = next_date
            return timedelta        

