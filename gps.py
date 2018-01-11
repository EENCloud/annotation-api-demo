import re
import requests
import time as t
import json
import argparse 
from gpsparse import prog_speed, parseLatLine, parseLonLine, getDateObjectForLine, TimeStepTracker
from eenclient import EENClient
from datetime import datetime, timedelta

# Parse the command line arguments
parser = argparse.ArgumentParser(description='App demonstating GPS data upload using the EEN Annotations API.')
parser.add_argument('apikey', metavar='a', type=str, nargs=1,help='key required for all api calls')
parser.add_argument('username', metavar='u', type=str, nargs=1,help='username')
parser.add_argument('password', metavar='p', type=str, nargs=1,help='password')
parser.add_argument('esn', metavar='e', type=str, nargs=1, help='camera device esn')
parser.add_argument('--namespace', nargs=1, type=int, default=[300])  #Default namespace for GPS data is 300.
parser.add_argument('--start',nargs=1,type=str, default=None)
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

# Open the GPS data file.
fp = open('gps.txt','r')

cnt = 0
points = []
step = TimeStepTracker()
uuid = None

print args.start
current_datetime_object = None  # Tracks the current timestamp of the annotation we will be posting to the API.
if args.start is not None:
    # override the starting timestamp in the GPS file with the one given in the command line args.
    current_datetime_object = datetime.strptime(args.start[0], '%Y%m%d%H%M%S')

while True:
    # Loop through the file one line at a time.
    line = fp.readline()
    if not line: break  # break the loop when we reach the end of file.
    
    #Current line should be a date string.  Convert it to a Python date object.
    datetime_object = getDateObjectForLine(line)
    if datetime_object:
        # Compute how much time elapsed since the last GPS reading.
        timedelta = step.getTimeDelta(datetime_object)

        if current_datetime_object is None:
            # set current_datetime_object the datetime_object if we didn't override the timestamp in the input args.
            current_datetime_object = datetime_object
        
        # increment the time and convert to EEN format.
        current_datetime_object = current_datetime_object + timedelta
        eents = current_datetime_object.strftime('%Y%m%d%H%M%S.000')
        
        # Read the longitude.
        l = fp.readline()
        lon_dd = parseLonLine(l)

        # Read the latitude.
        l = fp.readline()
        lat_dd = parseLatLine(l)

        # Read the velocity.
        l = fp.readline()
        res = prog_speed.match(l)
        data = {
           # "ts":eents,  # don't need timestamp here since the API will add it for us.
           "lat":lat_dd,
           "lon":lon_dd,
           # "vel":res.groups()[0]  # Don't save the velocity for now...  but could add it back later.
        }
        print data

        # Do we have an annotation yet?  If not, create one.
        if uuid is None:
            annt = client.createAnnotation(args.esn[0], eents, {'start':data}, args.namespace[0])
            if annt is None:
                print 'Failed to create annotations'
                exit()
            uuid = annt['uuid']
        else:
            # Update the annotation with the GPS data.   We are using the 'heartbeat' update type.
            # The API will create a '_hb' attribute in the annotation containing an array of data 
            # from all the update API calls.  These calls should be performed within 10 seconds of each other.
            # Otherwise, the annotation will be closed automatically and no future updates will be allowed.
            annt = client.updateAnnotation(uuid, args.esn[0], eents, data, args.namespace[0], 'hb')
            if annt is None:
                print 'Failed to update annotation??'
                exit()

        # Track how many annotation updates we have made.  For purposes of this demo, we only take the
        # first five GPS readings from the file.
        cnt = cnt + 1
        if cnt == 5:
            # Close the annotation
            # increment the time and convert to EEN format.
            current_datetime_object = current_datetime_object + timedelta
            eents = current_datetime_object.strftime('%Y%m%d%H%M%S.000')
            end_annt = client.updateAnnotation(uuid, args.esn[0], eents, {'end':'End of annotation.  Put extra data here.'}, args.namespace[0], 'end')
            t.sleep(2.0) # adding this to fix a timing issue.  Attempt to read back the annotation right away will fail
            break

        # simulate the heartbeat time interval.
        t.sleep(2.0)
        
        
# Read back the annotation using the API, display the results.
if uuid is not None:
    r = client.getAnnotations(args.esn[0], [uuid])
    print '--------------------'
    print json.dumps(r[0])
    exit()

