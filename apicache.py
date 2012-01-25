import time
import cPickle
import zlib
import os
from os.path import join, exists
##import tempfile
from noware.evetools.models import CachedRequest
import base64

# this is from mod_python, we're using mod_wsgi
##from noware.apachelogger import CustomApacheLogger

#from constants import APICACHE_PATH
##APICACHE_PATH = os.path.join(tempfile.gettempdir(), "eveapi")

class cache_handler(object):
    # adapted from http://home.wanadoo.nl/ntt/eve/library/files/api/apitest.py (does this satisfy the terms of the license?), will need work, but we need basic cache functionality... I feel guilty for abusing the server. FIXME --danny
    
    def __init__(self, debug=False):

        ##self.debug = debug
        self.debug = False

        self.count = 0
        self.cache = {}
        ##self.tempdir = APICACHE_PATH
        ##if not exists(self.tempdir):
        ##    os.makedirs(self.tempdir)

        ##self.apache_logger = CustomApacheLogger(self.debug)
        ##self.apache_logger.log("Created logging object (apicache).")
    
    def retrieve(self, host, path, params):
        # eveapi asks if we have this request cached
        key = hash((host, path, frozenset(params.items())))

        # for logging (but currently unused, to be removed)
        self.count += 1
        
        # see if we have the requested page cached...
        cached = self.cache.get(key, None)
        if cached:
            load_from_db = None
            ##cacheFile = None
        else:
            load_from_db = True
            ##self.apache_logger.log("%s: retrieving from database models." % path)
            # not in memory, maybe on disk --danny
            ##cacheFile = join(self.tempdir, str(key) + ".cache")
            ##if exists(cacheFile):
            ##    self.log("%s: retreiving from disk." % path)
            ##    f = open(cacheFile, "rb")
            ##    cached = self.cache[key] = cPickle.loads(zlib.decompress(f.read()))
            ##    f.close()
            result = CachedRequest.objects.filter(hash_key=key)
            if result:
                ##cached = self.cache[key] = cPickle.loads(zlib.decompress(base64.decodestring(result[0].pickled_data)))
                cached = self.cache[key] = cPickle.loads(base64.decodestring(result[0].pickled_data))

        if cached:

            # check if the cached object is fresh enough
            if time.time() < cached[0]:

                ##self.apache_logger.log("%s: returning cached document." % path)
                # return the cached object
                return cached[1]

            else:

                # if it's stale, purge it --danny
                ##self.apache_logger.log("%s: cache expired, purging!" % path)
                del self.cache[key]
                ##if cacheFile:
                ##    os.remove(cacheFile)
                if load_from_db and result:
                    result.delete()

        else:
            
            ##self.apache_logger.log("%s: not cached, fetching from server..." % path)
            # We didn't get a cache hit so return None to indicate that the data should be requested from server
            return None
    
    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item
        ##if not exists(self.tempdir):
        ##    os.makedirs(self.tempdir)
        
        key = hash((host, path, frozenset(params.items())))
        
        cachedFor = obj.cachedUntil - obj.currentTime
        if cachedFor:
            ##self.apache_logger.log("%s: cached (%d seconds)." % (path, cachedFor))

            cachedUntil = time.time() + cachedFor

            # store in memory
            cached = self.cache[key] = (cachedUntil, obj)
            
            # store in cache folder
            ##cacheFile = join(self.tempdir, str(key) + ".cache")
            ##f = open(cacheFile, "wb")
            ##f.write(zlib.compress(cPickle.dumps(cached, -1)))
            ##f.close
            ##obj_to_cache = CachedRequest(hash_key=key, pickled_data=base64.encodestring(zlib.compress(cPickle.dumps(cached, -1))))
            obj_to_cache = CachedRequest(hash_key=key, pickled_data=base64.encodestring(cPickle.dumps(cached, -1)))
            obj_to_cache.save()

