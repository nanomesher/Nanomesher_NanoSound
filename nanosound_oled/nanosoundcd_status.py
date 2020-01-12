from pymemcache.client.base import Client
from pymemcache import serde
from datetime import datetime
import os

last_report = None
last_ripping = False

def is_nanosoundcd_installed():
    return os.path.isdir("/home/volumio/nanomesher_nanosoundcd")


def to_display():
    global last_report, last_ripping
    res = is_rip_on_going()
    if (res[0] == True):
        if(last_report != res[2]):
            last_report = res[2]
            last_ripping = True
            return [True,res[1]]
        else:
            last_ripping = True
            return None
    else:
        if(last_ripping==True):
            #was ripping but now stopped
            last_ripping = False
            return [False,res[1]]
        else:
            last_ripping = False
            return None


def is_rip_on_going():
    client = Client(('localhost', 11211), serializer=serde.python_memcache_serializer,
                    deserializer=serde.python_memcache_deserializer)
    ripinfodict = client.get('ripprogress')
    if (ripinfodict <> None):

        if ('riplastupdate' in ripinfodict):
            riplastupdate = datetime.strptime(ripinfodict['riplastupdate'], "%Y-%m-%d %H:%M:%S")
            if ((((datetime.now() - riplastupdate).seconds) > 20)):
                return [False]
            elif ((((datetime.now() - riplastupdate).seconds) <= 20)):
                if ('albumname' in ripinfodict):
                    return [True, ripinfodict["albumname"], ripinfodict["ripstart"]]
                else:
                    return [True, "via NanoSound CD", ripinfodict["ripstart"]]
        else:
            return [False]
    else:
        return [False]
