# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import utils

#-----------------------------------------------------------------------------------------

__all__ = ['Expose', 'RawExpose', 'JsonExpose', 'JsonRender']

#-----------------------------------------------------------------------------------------

class ErrorData(object):
    def __init__(self, name, template, message):
        self.name = name
        self.template  = template
        self.message  = message

ERROR_LOGIN = ErrorData(u"LOGIN", "error_login", u"INICIO DE SESIÓN REQUERIDO")
ERROR_ROLES = ErrorData(u"ROLES", "error_roles", u"NO TIENE PRIVILEGIOS SUFICIENTES")
ERROR_VERBS = ErrorData(u"VERBS", "error_basic", u"ERROR DE ACCESO")

#-----------------------------------------------------------------------------------------

class Expose(object):
    
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
                if not page.checkUser():
                    return self.error(page, ERROR_LOGIN)
                
                # check auth conditions
                if not page.checkAuth(self.auth):
                    return self.error(page, ERROR_ROLES)
            
            # check verbs
            if not(page.request.method in self.verbs):
                return self.error(page, ERROR_VERBS)
            
            uri = page.request.path_info if (self.uri is None) else self.uri
            fout = f(page, *args, **kwargs)
            return self.render(fout, uri, **self.kwa)
        
        wrapper.__name__ = f.__name__
        wrapper.exposed = True
        return wrapper
    
    def error(self, page, err):
        return self.render({"page": page}, err.template)
    
    def render(self, fout, uri=None, **kwa):
        fout.update(kwa)
        return utils.lookup.render(uri, **fout)

#-----------------------------------------------------------------------------------------

class RawExpose(Expose):
    
    def error(self, page, err):
        txt = u"%s: %s" % (err.name, err.message)
        raise page.httperror(403, txt.encode("utf-8"))
    
    def render(self, fout, uri=None, **kwa):
        return fout

#-----------------------------------------------------------------------------------------

class JsonExpose(Expose):
    
    def error(self, page, err):
        sal = dict(ok=False, err=err.name, msg=err.message)
        return utils.toJson(**sal)
    
    def render(self, fout, uri=None, **kwa):
        fout.update(kwa)
        fout.update(ok=True, err="")
        return utils.toJson(**fout)

#-----------------------------------------------------------------------------------------

class JsonRender(Expose):
    
    def __init__(self, verbs="GET,POST", auth=None, uri=None, cache=False, inline=False, **kwa):
        Expose.__init__(self, verbs, auth, uri, **kwa)
        self.cache = cache
        self.inline = inline
    
    def error(self, page, err):
        cache = False if err == ERROR_VERBS else True
        
        data = u"[ERROR: %s]" % err.name
        if self.inline is False:
            data=utils.lookup.render(err.template, **{"page": page})
        
        sal = dict(ok=False, err=err.name, msg=err.message, cache=cache, data=data)
        return utils.toJson(**sal)
    
    def render(self, fout, uri=None, **kwa):
        fout.update(kwa)
        sal = dict(ok=True, err="", msg="", cache=self.cache, 
            data=utils.lookup.render(uri, **fout)
        )
        return utils.toJson(**sal)
