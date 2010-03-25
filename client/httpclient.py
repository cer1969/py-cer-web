# -*- coding: utf-8 -*-

import cookielib, urllib, urllib2

try:
    import simplejson as json
except ImportError:
    import json

#-----------------------------------------------------------------------------------------

__all__ = ['Response', 'URL_ERROR', 'HTTP_ERROR', 'HTTPClient']

#-----------------------------------------------------------------------------------------

URL_ERROR = "URL_ERROR"
HTTP_ERROR = "HTTP_ERROR"

class Response(object):
    def __init__(self, data=None, ok=True, err=None, code=None):
        self.data = data
        self.ok = ok
        self.err = err
        self.code = code

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
        self._online = False
        
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
    
    def _isOnline(self):
        return self._online
    online = property(_isOnline)
    
    def _fixurl(self, url):
        return "%s%s" % (self.home, url)
    
    def _unjson(self, r):
        if not (r.data is None):
            d = json.loads(r.data)
            r.data = AttrDict(d)
        return r
    
    def open(self, request):
        self._online = True
        try:
            r = self.opener.open(request)
            return Response(r.read())
        except urllib2.HTTPError, e:
            return Response(None, False, HTTP_ERROR, e.code)
        except urllib2.URLError, e:
            self._online = False
            return Response(None, False, URL_ERROR, e.reason.errno)
    
    def get(self, url):
        return self.open(self._fixurl(url))
    
    def jget(self, url):
        return self._unjson(self.get(url))
    
    def post(self, url, **kw):
        data = urllib.urlencode(kw)
        request = urllib2.Request(self._fixurl(url), data)
        return self.open(request)
    
    def jpost(self, url, **kw):
        return self._unjson(self.post(url, **kw))
    
    def close(self):
        self.opener.close()
        self._online = False