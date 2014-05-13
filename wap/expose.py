# CRISTIAN ECHEVERRÍA RABÍ

from .constants import (ERROR_LOGIN, ERROR_ROLES, ERROR_VERBS,
                       FMT_RAW, FMT_TPL, FMT_JSON, FMT_JSONTPL)

#-----------------------------------------------------------------------------------------

__all__ = []

#-----------------------------------------------------------------------------------------

class BaseExpose(object):
    """ Abstract class for decorator that expose methods of wap.Handler instances
    """
    
    def __init__(self, verbs="GET,POST", auth=None, uri=None, fmt=None):
        self.verbs = [x.strip().upper() for x in verbs.split(",")]
        self.auth = auth
        self.uri = uri
        self.fmt = fmt
    
    def __call__(self, f):
        def wrapper(handler, *args, **kwargs):
            
            # Unifica auth definidos a nivel de clase y métodos
            auth = getattr(handler, "auth", None)
            if auth is None:
                auth = self.auth
            else:
                auth = auth if (self.auth is None) else auth.extend(self.auth)
            
            # check auth
            if not (auth is None):
                
                # check auth login
                if not handler.checkUser():
                    return handler.error(self.fmt, ERROR_LOGIN)
                
                # check auth conditions
                if not handler.checkAuth(auth):
                    return handler.error(self.fmt, ERROR_ROLES)
            
            # check verbs
            if not(handler.request.method in self.verbs):
                return handler.error(self.fmt, ERROR_VERBS)
            
            fout = f(handler, *args, **kwargs)
            uri = handler.request.path_info if (self.uri is None) else self.uri
            return handler.send(self.fmt, uri, fout)
        
        wrapper.__name__ = f.__name__
        wrapper.exposed = True
        return wrapper


#-----------------------------------------------------------------------------------------

class Raw(BaseExpose):
    def __init__(self, verbs="GET,POST", auth=None):
        super(Raw, self).__init__(verbs, auth, None, FMT_RAW)

class Template(BaseExpose):
    def __init__(self, verbs="GET,POST", auth=None, uri=None):
        super(Template, self).__init__(verbs, auth, uri, FMT_TPL)

class Json(BaseExpose):
    def __init__(self, verbs="GET,POST", auth=None):
        super(Json, self).__init__(verbs, auth, None, FMT_JSON)

class JsonTemplate(BaseExpose):
    def __init__(self, verbs="GET,POST", auth=None, uri=None):
        super(JsonTemplate, self).__init__(verbs, auth, uri, FMT_JSONTPL)
    