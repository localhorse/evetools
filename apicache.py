import time
import cPickle
import zlib
import os
from os.path import join, exists

from noware.evetools.models import CachedRequest
import base64

class cache_handler(object):
    # adapted from http://home.wanadoo.nl/ntt/eve/library/files/api/apitest.py (does this satisfy the terms of the license?), will need work, but we need basic cache functionality... I feel guilty for abusing the server. FIXME --danny
    
    def __init__(self, debug=False):

        ##self.debug = debug
        self.debug = False

        self.count = 0
        self.cache = {}
    
    def retrieve(self, host, path, params):
        # eveapi asks if we have this request cached
        key = hash((host, path, frozenset(params.items())))

        # for logging (but currently unused, to be removed)
        self.count += 1
        
        # see if we have the requested page cached...
        cached = self.cache.get(key, None)
        if cached:
            load_from_db = None
        else:
            load_from_db = True
            result = CachedRequest.objects.filter(hash_key=key)
            if result:
                cached = self.cache[key] = cPickle.loads(base64.decodestring(result[0].pickled_data))

        if cached:

            # check if the cached object is fresh enough
            if time.time() < cached[0]:
                # return the cached object
                return cached[1]

            else:

                # if it's stale, purge it --danny
                del self.cache[key]
                if load_from_db and result:
                    result.delete()

        else:
            
            # We didn't get a cache hit so return None to indicate that the data should be requested from server
            return None
    
    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item
        
        key = hash((host, path, frozenset(params.items())))
        
        cachedFor = obj.cachedUntil - obj.currentTime
        if cachedFor:

            cachedUntil = time.time() + cachedFor

            # store in memory
            cached = self.cache[key] = (cachedUntil, obj)
            
            # store in Django DB
            obj_to_cache = CachedRequest(hash_key=key, pickled_data=base64.encodestring(cPickle.dumps(cached, -1)))
            obj_to_cache.save()

