import time as t
import json
import argparse 
from eenclient import EENClient

# Parse the command line arguments
parser = argparse.ArgumentParser(description='App demonstating Annotations List API.')
parser.add_argument('apikey', metavar='api_key', type=str, nargs=1,help='key required for all api calls')
parser.add_argument('username', metavar='user', type=str, nargs=1,help='username')
parser.add_argument('password', metavar='pwd', type=str, nargs=1,help='password')
parser.add_argument('esn', metavar='esn', type=str, nargs=1, help='camera device esn')
parser.add_argument('start', metavar='start', type=str, nargs=1, help='start timestamp')
parser.add_argument('end', metavar='end', type=str, nargs=1, help='end timestamp')
parser.add_argument('--namespace', nargs='+', type=int)  #Default namespace for GPS data is 300.

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

print args

# # Fetch the device to make sure the ESN is valid.
annts = client.getAnnotationsList(args.esn[0], args.start[0], args.end[0])
if annts is None:
     print 'Failed to get annotations for device: {}'.format(args.esn[0])
     exit()

print '------------------------------'
print annts

