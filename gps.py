import re
import requests
import time as t
import json
import argparse
from gpsparse import lon_to_decimal, lat_to_decimal
from eenclient import EENClient
from datetime import datetime, timedelta

# Parse the command line arguments
parser = argparse.ArgumentParser(description='App demonstating GPS data upload using the EEN Annotations API.')
parser.add_argument('apikey', metavar='a', type=str, nargs=1,help='key required for all api calls')
parser.add_argument('username', metavar='u', type=str, nargs=1,help='username')
parser.add_argument('password', metavar='p', type=str, nargs=1,help='password')
parser.add_argument('esn', metavar='e', type=str, nargs=1, help='camera device esn')
parser.add_argument('--namespace', nargs=1, type=int, default=[300])  #Default namespace for GPS data is 300.
parser.add_argument('--start',nargs=1,type=str)
args = parser.parse_args()

# Setup the API client
client = EENClient(args.apikey[0])

# Login using the credentials provide in the arguments.  This is a two step 
# process for non-two-factor users: authenticate and authorize.  This app does 
# not support two-factor authentication currently.
token = client.authenticate(args.username[0], args.password[0])
if token is None:
    print 'Login failed.'
    exit()

user = client.authorize(token)
if user is None:
    print 'Failed to authorize user.'
    exit()

# Fetch the device to make sure the ESN is valid.
device = client.getDevice(args.esn[0])
if device is None:
    print 'Failed to get device: {}'.format(esn)
    exit()


# Define regular expressions to assist us in parsing the GPS file
# Regex to match lines with timestamp information
prog_ts = re.compile('\[(\d+-\d+-\d+)\s+-\s+(\d+:\d+:\d+)')
# Regex to match lines with latitude and longitude information
prog_lat_lon = re.compile('^\s*(.+)\xa1\xe3(.+)\'(.+)" ([EWSN])')
# Regex to match lines containing speed information
prog_speed = re.compile('Speed:\s*(\S+)\s*KPH')

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


fp = open('gps.txt','r')

cnt = 0
points = []
step = TimeStepTracker()

current_datetime_object = None
if args.start[0] is not None:
    current_datetime_object = datetime.strptime(args.start[0], '%Y%m%d%H%M%S')
    
while True:
    # Loop through the file one line at a time.
    line = fp.readline()
    if not line: break  # break the loop when we reach the end of file.
        
    datetime_object = getDateObjectForLine(line)
    if datetime_object:
        timedelta = step.getTimeDelta(datetime_object)
        
        if current_datetime_object is None:
            current_datetime_object = datetime_object
        
        current_datetime_object = current_datetime_object + timedelta
        
        eents = current_datetime_object.strftime('%Y%m%d%H%M%S.000')
        
        # Read the longitude.
        l = fp.readline()
        lon_res = prog_lat_lon.match(l)
        lon = lon_res.groups()
        lon_dd = lon_to_decimal(float(lon[0]),float(lon[1]),float(lon[2]),lon[3])

        # Read the latitude.
        l = fp.readline()
        lat_res = prog_lat_lon.match(l)
        lat = lat_res.groups()
        lat_dd = lat_to_decimal(float(lat[0]),float(lat[1]),float(lat[2]),lat[3])

        # Read the velocity.
        l = fp.readline()
        res = prog_speed.match(l)
        data = {
           "ts":eents,
           "lat":lat_dd,
           "lon":lon_dd,
           "vel":res.groups()[0]
        }
        print data

        annt = client.createAnnotation(args.esn[0], eents, data, args.namespace[0])
        if annt is None:
             print 'Failed to create annotations'
             exit()
        else:
             print annt
             uuid = annt['uuid']
             print uuid
             t.sleep(1.0) # adding this to fix a timing issue.  Attempt to read back the annotation right away will fail
             r = client.getAnnotations(args.esn[0], [uuid]) #['ff4f9566-f251-11e7-971f-06936ec4fa5b']) [annt['uuid']])
             print '--------------------'
             print r
             exit()
        
        cnt = cnt + 1
        
        if cnt == 1:
            exit()
        
        # print t.sleep(0.50)
