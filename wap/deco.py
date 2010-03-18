# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
import utils

#-----------------------------------------------------------------------------------------

__all__ = ['cpexpose', 'HTTPRedirect', 'AbstractDecorator', 'AbstractExpose', 'Expose',
           'JsonExpose']

#-----------------------------------------------------------------------------------------
# Alias de cherrypy

cpexpose = cherrypy.expose
HTTPRedirect = cherrypy.HTTPRedirect

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

class AbstractExpose(AbstractDecorator):
    """ Decorator for exposing content, checks verbs and optional authentication.
        The instance with de decorated method must have:
        - Attributes: user and pathInfo
    """
    
    def __init__(self, verbs="GET,POST", auth=None):
        AbstractDecorator.__init__(self)
        
        self._verbs = [x.strip().upper() for x in verbs.split(",")]
        
        self._authreq = False if (auth is None) else True
        self._conds = []
        
        if self._authreq:
            if isinstance(auth, list):
                self._conds = auth
            else:
                self._conds.append(auth)
    
    def verbsError(self, obj):
        raise NotImplementedError("This is an abstract class")
    
    def loginError(self, obj):
        raise NotImplementedError("This is an abstract class")
    
    def roleError(self, obj):
        raise NotImplementedError("This is an abstract class")
    
    def getResult(self, data, obj):
        raise NotImplementedError("This is an abstract class")
    
    def getWrapper(self, func):
        def wrapper(obj, *args, **kwargs):
            
            # verbs check
            if not(cherrypy.request.method in self._verbs):
                return self.verbsError(obj)
            
            # auth check
            if self._authreq:
                if obj.user is None:
                    return self.loginError(obj)
                if not utils.checkConditions(obj.user, self._conds):
                    return self.roleError(obj)
            
            return self.getResult(func(obj, *args, **kwargs), obj)
        
        wrapper.exposed = True
        return wrapper

#-----------------------------------------------------------------------------------------

class Expose(AbstractExpose):
    """ Decorator for exposing content, optional rendering using template and
        optional authentication.
        The instance with de decorated method must have:
        - Attributes: user and pathInfo
        - Templates: basic_error, login and role_error
    """
    
    def __init__(self, verbs="GET,POST", auth=None, uri=None, **kwa):
        AbstractExpose.__init__(self, verbs, auth)
        self._uri = uri
        self._kwa = kwa
    
    def verbsError(self, obj):
        print u"%s Error de método: %s" % (obj.pathInfo, cherrypy.request.method)
        return utils.lookup.render("basic_error", page=obj)
    
    def loginError(self, obj):
        return utils.lookup.render("login", page=obj)
    
    def roleError(self, obj):
        return utils.lookup.render("role_error", page=obj)
    
    def getResult(self, data, obj):
        if not isinstance(data, dict):
            return data
        data.update(self._kwa)
        uri = obj.pathInfo if (self._uri is None) else self._uri
        return utils.lookup.render(uri, **data)


#-----------------------------------------------------------------------------------------

class JsonExpose(AbstractExpose):
    """ Decorator for exposing content returning json data with optional authentication.
        The instance with de decorated method must have:
        - Attributes: user and pathInfo
    """
    
    def verbsError(self, obj):
        print u"%s Error de método: %s" % (obj.pathInfo, cherrypy.request.method)
        return utils.toJson(json_ok=False, json_err=u"VERBS")
    
    def loginError(self, obj):
        print u"%s Error: Login requerido" % obj.pathInfo
        return utils.toJson(json_ok=False, json_err=u"LOGIN")
    
    def roleError(self, obj):
        print u"%s Error: Restricción de usuario" % obj.pathInfo
        return utils.toJson(json_ok=False, json_err=u"ROLE")
    
    def getResult(self, data, obj):
        try:
            sal = dict(json_ok=True, json_err=u"")
            if isinstance(data, dict):
                sal.update(data)
            else:
                sal["json_data"] = data
            return utils.toJson(**sal)
        except Exception, e:
            print u"%s Error: %s" % (obj.pathInfo, e)
            return utils.toJson(json_ok=False, json_err=u"APP")