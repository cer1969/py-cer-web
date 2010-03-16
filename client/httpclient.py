# -*- coding: utf-8 -*-

import cookielib, urllib, urllib2

try:
    import simplejson as json
except ImportError:
    import json

#-----------------------------------------------------------------------------------------

__all__ = ['HTTPClient']

#-----------------------------------------------------------------------------------------

class AttrDict(dict):
    
    def __getattr__(self, name):
        return self[name]
    
    def __setattr__(self, name, value):
        self[name] = value

#-----------------------------------------------------------------------------------------

class HTTPClient(object):
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.home = "http://%s:%d" % (host, port)
        
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
    
    def _fixUrl(self, url):
        return "%s%s" % (self.home, url)
    
    def get(self, url):
        r = self.opener.open(self._fixUrl(url))
        return r.read()
    
    def jget(self, url):
        sal = json.loads(self.get(url))
        return AttrDict(sal)
    
    def post(self, url, **kw):
        data = urllib.urlencode(kw)
        request = urllib2.Request(self._fixUrl(url), data)
        r = self.opener.open(request)
        return r.read()
    
    def jpost(self, url, **kw):
        sal = json.loads(self.post(url, **kw))
        return AttrDict(sal)
    
    def close(self):
        self.opener.close()