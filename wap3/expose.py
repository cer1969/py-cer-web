# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
from utils import (ERROR_LOGIN, ERROR_ROLES, ERROR_VERBS,
                   FMT_RAW, FMT_TPL, FMT_JSON, FMT_JSONTPL)

#-----------------------------------------------------------------------------------------

__all__ = []

#-----------------------------------------------------------------------------------------

def wap_verbs(verbs, fmt, kwa):
    root = cherrypy.request.app.root
    verbs = [x.strip().upper() for x in verbs.split(",")]
    if not(cherrypy.request.method in verbs):
        return root.error(ERROR_VERBS, fmt,  **kwa)

def wap_auth(auth, fmt, kwa):
    root = cherrypy.request.app.root
    
    # check auth
    if auth is None:
        return
    
    # check auth login
    if not root.checkUser():
        return root.error(ERROR_LOGIN, fmt, **kwa)
    
    # check auth conditions
    if not root.checkAuth(auth):
        return root.error(ERROR_ROLES, fmt, **kwa)


def wap_render(uri, fmt, kwa):
    root = cherrypy.request.app.root
    uri = cherrypy.request.path_info if (uri is None) else uri
    fout = cherrypy.request.handler()
    def newHandler(): return root.render(fout, uri, fmt, **kwa)
    cherrypy.request.handler = newHandler

cherrypy.tools.wap_verbs = cherrypy.Tool('on_start_resource', wap_verbs)
#cherrypy.tools.wap_auth = cherrypy.Tool('before_request_body', wap_auth)
cherrypy.tools.wap_auth = cherrypy.Tool('before_handler', wap_auth, priority=20)
cherrypy.tools.wap_render = cherrypy.Tool('before_handler', wap_render, priority=40)

#-----------------------------------------------------------------------------------------

class BaseExpose(object):
    
    def __init__(self, verbs=None, auth=None, uri=None, fmt=None, **kwa):
        cf = {}
        cf["tools.wap_render.on"] = True
        cf["tools.wap_render.uri"] = uri
        cf["tools.wap_render.fmt"] = fmt
        cf["tools.wap_render.kwa"] = kwa
        if verbs:
            cf["tools.wap_verbs.on"] = True
            cf["tools.wap_verbs.verbs"] = verbs
            cf["tools.wap_verbs.fmt"] = fmt
            cf["tools.wap_verbs.kwa"] = kwa
        if not (auth is None):
            cf["tools.wap_auth.on"] = True
            cf["tools.wap_auth.auth"] = auth
            cf["tools.wap_auth.fmt"] = fmt
            cf["tools.wap_auth.kwa"] = kwa
        self._cf = cf
    
    def __call__(self, f):
        f.exposed = True
        f._cp_config = self._cf
        return f


#-----------------------------------------------------------------------------------------

class Raw(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None, **kwa):
        super(Raw, self).__init__(verbs, auth, uri, FMT_RAW, **kwa)

class Template(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None, **kwa):
        super(Template, self).__init__(verbs, auth, uri, FMT_TPL, **kwa)

class Json(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None, **kwa):
        super(Json, self).__init__(verbs, auth, uri, FMT_JSON, **kwa)

class JsonTemplate(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None, inline=False, **kwa):
        kwa.update(inline=inline)
        super(JsonTemplate, self).__init__(verbs, auth, uri, FMT_JSONTPL, **kwa)
    