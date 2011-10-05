# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
from utils import (ERROR_LOGIN, ERROR_ROLES, ERROR_VERBS,
                   FMT_RAW, FMT_TPL, FMT_JSON, FMT_JSONTPL)

#-----------------------------------------------------------------------------------------

__all__ = []

#-----------------------------------------------------------------------------------------

def wap_verbs(verbs, fmt):
    root = cherrypy.request.app.root
    verbs = [x.strip().upper() for x in verbs.split(",")]
    if not(cherrypy.request.method in verbs):
        return root.error(ERROR_VERBS, fmt)

def wap_auth(auth, fmt):
    root = cherrypy.request.app.root
    
    error = None
    cherrypy.request._skiprender = False
    
    # check auth
    if auth is None:
        return
    
    # check auth login
    if not root.checkUser():
        error = ERROR_LOGIN
        #cherrypy.request._skiprender = True
        #return root.error(ERROR_LOGIN, fmt)
    
    # check auth conditions
    if not root.checkAuth(auth):
        error = ERROR_ROLES
        #cherrypy.request._skiprender = True
        #return root.error(ERROR_ROLES, fmt)
    
    if not (error is None):
        cherrypy.request._skiprender = True
        cherrypy.request.handler = lambda: root.error(error, fmt)
    


def wap_render(uri, fmt):
    if hasattr(cherrypy.request, "_skiprender") and cherrypy.request._skiprender:
        return
    root = cherrypy.request.app.root
    uri = cherrypy.request.path_info if (uri is None) else uri
    fout = cherrypy.request.handler()
    cherrypy.request.handler = lambda: root.render(fout, uri, fmt)

cherrypy.tools.wap_verbs = cherrypy.Tool('on_start_resource', wap_verbs)
#cherrypy.tools.wap_auth = cherrypy.Tool('before_request_body', wap_auth)
cherrypy.tools.wap_auth = cherrypy.Tool('before_handler', wap_auth, priority=20)
cherrypy.tools.wap_render = cherrypy.Tool('before_handler', wap_render, priority=40)

#-----------------------------------------------------------------------------------------

class BaseExpose(object):
    
    def __init__(self, verbs=None, auth=None, uri=None, fmt=None):
        cf = {}
        cf["tools.wap_render.on"] = True
        cf["tools.wap_render.uri"] = uri
        cf["tools.wap_render.fmt"] = fmt
        if verbs:
            cf["tools.wap_verbs.on"] = True
            cf["tools.wap_verbs.verbs"] = verbs
            cf["tools.wap_verbs.fmt"] = fmt
        if not (auth is None):
            cf["tools.wap_auth.on"] = True
            cf["tools.wap_auth.auth"] = auth
            cf["tools.wap_auth.fmt"] = fmt
        self._cf = cf
    
    def __call__(self, f):
        f.exposed = True
        f._cp_config = self._cf
        return f


#-----------------------------------------------------------------------------------------

class Raw(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None):
        super(Raw, self).__init__(verbs, auth, uri, FMT_RAW)

class Template(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None):
        super(Template, self).__init__(verbs, auth, uri, FMT_TPL)

class Json(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None):
        super(Json, self).__init__(verbs, auth, uri, FMT_JSON)

class JsonTemplate(BaseExpose):
    def __init__(self, verbs=None, auth=None, uri=None):
        super(JsonTemplate, self).__init__(verbs, auth, uri, FMT_JSONTPL)
