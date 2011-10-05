# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

from utils import (ERROR_LOGIN, ERROR_ROLES, ERROR_VERBS,
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
            
            # check auth
            if not (self.auth is None):
                
                # check auth login
                if not handler.checkUser():
                    return handler.error(ERROR_LOGIN, self.fmt)
                
                # check auth conditions
                if not handler.checkAuth(self.auth):
                    return handler.error(ERROR_ROLES, self.fmt)
            
            # check verbs
            if not(handler.request.method in self.verbs):
                return handler.error(ERROR_VERBS, self.fmt)
            
            fout = f(handler, *args, **kwargs)
            uri = handler.request.path_info if (self.uri is None) else self.uri
            return handler.render(fout, uri, self.fmt)
        
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
    