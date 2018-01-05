
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
