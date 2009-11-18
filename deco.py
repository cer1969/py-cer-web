# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
import utils

#-----------------------------------------------------------------------------------------

__all__ = ['AbstractDecorator', 'Expose']

#-----------------------------------------------------------------------------------------

class AbstractDecorator(object):
    """ Abstract base class for page handler decorators
        Derived classes must overwrite getWrapper method
    """
    
    def getWrapper(self, func):
        raise NotImplementedError("This is an abstract class")
    
    def __call__(self, func):
        wrapper = self.getWrapper(func)
        if hasattr(func, "exposed"):
            wrapper.exposed = func.exposed
        wrapper.__name__ = func.__name__
        return wrapper

#-----------------------------------------------------------------------------------------

class Expose(AbstractDecorator):
    """ Decorator for exposing content, optional rendering using template and
        optional authentication.
        The instance with de decorated method must have:
        - Attributes: user and path_info
        - Templates: basic_error, login and role_error
    """
    
    def __init__(self, verbs="GET", auth=None, uri=None, **kwa):
        AbstractDecorator.__init__(self)
        
        self._verbs = [x.strip().upper() for x in verbs.split(",")]
        
        self._authreq = False if (auth is None) else True
        self._conds = []
        
        if self._authreq:
            if isinstance(auth, list):
                self._conds = auth
            else:
                self._conds.append(auth)
        
        self._uri = uri
        self._kwa = kwa
    
    def getWrapper(self, func):
        def wrapper(obj, *args, **kwargs):
            
            # verbs check
            if not(cherrypy.request.method in self._verbs):
                print u"%s Error de método: %s" % (obj.path_info, cherrypy.request.method)
                return utils.lookup.render("basic_error", page=obj)
            
            # auth check
            if self._authreq:
                if obj.user is None:
                    return utils.lookup.render("login", page=obj)
                
                if not utils.check_conditions(obj.user, self._conds):
                    return utils.lookup.render("role_error", page=obj)
            
            try:
                result = func(obj, *args, **kwargs)
                if not isinstance(result, dict):
                    return result
                result.update(self._kwa)
                uri = obj.path_info if (self._uri is None) else self._uri
                return utils.lookup.render(uri, **result)
            except Exception, e:
                print u"%s Error: %s" % (obj.path_info, e)
                return utils.lookup.render("basic_error", page=obj)
        
        wrapper.exposed = True
        return wrapper