# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

try:
    import simplejson as json
except ImportError:
    import json
from utils import lookup

#-----------------------------------------------------------------------------------------

__all__ = ['BaseExpose', 'Raw', 'Template', 'Json', 'JsonTemplate']

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

class BaseExpose(object):
    """ Abstract class for decorator that expose methods of wap.Page instances
    """
    
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
        raise NotImplementedError("this is an abstract class!")
    
    def render(self, fout, uri=None, **kwa):
        raise NotImplementedError("this is an abstract class!")

#-----------------------------------------------------------------------------------------

class Raw(BaseExpose):
    """ Exposes direct results and permits calls to redirect and httperror
    """
    
    def error(self, page, err):
        txt = u"%s: %s" % (err.name, err.message)
        raise page.httperror(403, txt.encode("utf-8"))
    
    def render(self, fout, uri=None, **kwa):
        return fout

#-----------------------------------------------------------------------------------------

class Template(BaseExpose):
    """ Receives dict from methods and returns a proceseced mako templates
    """
    
    def error(self, page, err):
        return self.render({"page": page}, err.template)
    
    def render(self, fout, uri=None, **kwa):
        fout.update(kwa)
        return lookup.render(uri, **fout)

#-----------------------------------------------------------------------------------------

class Json(BaseExpose):
    """ Receives dict from methods and returns json
    """
    
    def error(self, page, err):
        sal = dict(ok=False, err=err.name, msg=err.message)
        return json.dumps(sal)
    
    def render(self, fout, uri=None, **kwa):
        fout.update(kwa)
        fout.update(ok=True, err="")
        return json.dumps(fout)

#-----------------------------------------------------------------------------------------

class JsonTemplate(BaseExpose):
    """ Receives dict from methods and returns json with proceseced mako templates
    """
    
    def __init__(self, verbs="GET,POST", auth=None, uri=None, inline=False, **kwa):
        BaseExpose.__init__(self, verbs, auth, uri, **kwa)
        self.inline = inline
    
    def error(self, page, err):
        data = u"[ERROR: %s]" % err.name
        if self.inline is False:
            data=lookup.render(err.template, **{"page": page})
        
        sal = dict(ok=False, err=err.name, msg=err.message, data=data)
        return json.dumps(sal)
    
    def render(self, fout, uri=None, **kwa):
        fout.update(kwa)
        sal = dict(ok=True, err="", msg="", data=lookup.render(uri, **fout))
        return json.dumps(sal)
