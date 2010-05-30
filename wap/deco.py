# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import utils

#-----------------------------------------------------------------------------------------

__all__ = ['RawExpose', 'Expose', 'JsonExpose']

#-----------------------------------------------------------------------------------------

ERR_MSG_LOGIN = u"INICIO DE SESIÓN REQUERIDO"
ERR_MSG_ROLE  = u"NO TIENE PRIVILEGIOS SUFICIENTES"
ERR_MSG_VERBS = u"ERROR DE ACCESO"

#-----------------------------------------------------------------------------------------

class AbstractExpose(object):
    
    def __init__(self, verbs="GET,POST", auth=None, uri=None, **kwa):
        self.verbs = [x.strip().upper() for x in verbs.split(",")]
        self.auth = auth
        self.uri = uri
        self.kwa = kwa
    
    def __call__(self, f):
        def wrapper(page, *args, **kwargs):
            
            # check auth
            if not (self.auth is None):
                
                # check auth login
                if page.user is None:
                    return self.error(page, u"LOGIN", "error_login", ERR_MSG_LOGIN)
                
                # check auth roles
                if not page.checkUser(self.auth):
                    return self.error(page, u"ROLE", "error_role", ERR_MSG_ROLE)
            
            # check verbs
            if not(page.request.method in self.verbs):
                return self.error(page, u"VERBS", "error_basic", ERR_MSG_VERBS)
            
            return self.response(page, f(page, *args, **kwargs))
        
        wrapper.__name__ = f.__name__
        wrapper.exposed = True
        return wrapper
    
    def response(self, page, data):
        uri = page.request.path_info if (self.uri is None) else self.uri
        return self.render(data, uri, **self.kwa)
    
    def error(self, page, err, tpl, msg):
        raise NotImplementedError("This is an abstract class")
    
    def render(self, data, uri=None, **kwa):
        raise NotImplementedError("This is an abstract class")

#-----------------------------------------------------------------------------------------

class RawExpose(AbstractExpose):
    
    def error(self, page, err, tpl, msg):
        txt = u"%s: %s" % (err, msg)
        raise page.httperror(403, txt.encode("utf-8"))
    
    def render(self, data, uri=None, **kwa):
        return data

#-----------------------------------------------------------------------------------------
# Expose objest using Mako for rendering

class Expose(AbstractExpose):
    
    def error(self, page, err, tpl, msg):
        if page.request.method == "GET":
            return self.render({"page": page}, tpl)
        else:
            return self.render({"msg": msg}, "error_post")
    
    def render(self, data, uri=None, **kwa):
        data.update(kwa)
        return utils.lookup.render(uri, **data)

#-----------------------------------------------------------------------------------------

class JsonExpose(AbstractExpose):
    
    def error(self, page, err, tpl, msg):
        data = dict(ok=False, err=err, msg=msg)
        return self.render(data)
    
    def render(self, data, uri=None, **kwa):
        data.update(kwa)
        data.setdefault("ok", True)
        data.setdefault("err", "")
        data.setdefault("msg", "")
        return utils.toJson(**data)