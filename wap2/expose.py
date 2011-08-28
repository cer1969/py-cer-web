# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

#-----------------------------------------------------------------------------------------

__all__ = ['BaseExpose', 'ERROR_LOGIN', 'ERROR_ROLES', 'ERROR_VERBS']

#-----------------------------------------------------------------------------------------

ERROR_LOGIN = u"LOGIN"
ERROR_ROLES = u"ROLES"
ERROR_VERBS = u"VERBS"

#-----------------------------------------------------------------------------------------

class BaseExpose(object):
    """ Abstract class for decorator that expose methods of wap.Handler instances
    """
    
    def __init__(self, verbs="GET,POST", auth=None, uri=None, **kwa):
        self.verbs = [x.strip().upper() for x in verbs.split(",")]
        self.auth = auth
        self.uri = uri
        self.kwa = kwa
    
    def __call__(self, f):
        def wrapper(handler, *args, **kwargs):
            
            # check auth
            if not (self.auth is None):
                
                # check auth login
                if not handler.checkUser():
                    return self.error(handler, ERROR_LOGIN)
                
                # check auth conditions
                if not handler.checkAuth(self.auth):
                    return self.error(handler, ERROR_ROLES)
            
            # check verbs
            if not(handler.request.method in self.verbs):
                return self.error(handler, ERROR_VERBS)
            
            fout = f(handler, *args, **kwargs)
            return self.render(handler, fout)
        
        wrapper.__name__ = f.__name__
        wrapper.exposed = True
        return wrapper
    
    def error(self, handler, err):
        raise NotImplementedError("this is an abstract class!")
    
    def render(self, handler, fout):
        raise NotImplementedError("this is an abstract class!")

#-----------------------------------------------------------------------------------------

class Raw(BaseExpose):
    """ Exposes direct results and permits calls to redirect and httperror
    """
    def error(self, handler, err):
        return handler.errorRaw(err)
    
    def render(self, handler, fout):
        return handler.renderRaw(fout)

#-----------------------------------------------------------------------------------------

class Template(BaseExpose):
    """ Receives dict from methods and returns a proceseced mako templates
    """
    def error(self, handler, err):
        return handler.errorTemplate(err)
    
    def render(self, handler, fout):
        uri = handler.request.path_info if (self.uri is None) else self.uri
        return handler.renderTemplate(fout, uri, **self.kwa)

#-----------------------------------------------------------------------------------------

class Json(BaseExpose):
    """ Receives dict from methods and returns json
    """
    def error(self, handler, err):
        return handler.errorJson(err)
    
    def render(self, handler, fout):
        return handler.renderJson(fout, **self.kwa)

#-----------------------------------------------------------------------------------------

class JsonTemplate(BaseExpose):
    """ Receives dict from methods and returns json with proceseced mako templates
    """
    def __init__(self, verbs="GET,POST", auth=None, uri=None, inline=False, **kwa):
        BaseExpose.__init__(self, verbs, auth, uri, **kwa)
        self.inline = inline
    
    def error(self, handler, err):
        return handler.errorJsonTemplate(err, self.inline)
    
    def render(self, handler, fout):
        uri = handler.request.path_info if (self.uri is None) else self.uri
        return handler.renderJsonTemplate(fout, uri, **self.kwa)
    