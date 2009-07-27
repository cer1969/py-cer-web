# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
import utils

#-----------------------------------------------------------------------------------------

__all__ = ['AbstractDecorator', 'Expose', 'FxExpose', 
           'Auth', 'Template', 'ExposeOld']

#-----------------------------------------------------------------------------------------

class AbstractDecorator(object):
    """ Abstract base class for page handler decorators
        Derived classes must overwrite getWrapper method
    """
    
    def getWrapper(self, func):
        raise utils.WebException("This is an abstract class")
    
    def __call__(self, func):
        wrapper = self.getWrapper(func)
        if hasattr(func, "exposed"):
            wrapper.exposed = func.exposed
        wrapper.__name__ = func.__name__
        return wrapper

#-----------------------------------------------------------------------------------------

class Auth(AbstractDecorator):
    """ Decorator for user authentication
        The instance with de decorated method must have a 'user' attribute
        and an optional 'conditions' attribute
    """
    
    def __init__(self, conditions=None):
        AbstractDecorator.__init__(self)
        self._conditions = conditions
    
    def getWrapper(self, func):
        def wrapper(obj, *args, **kwargs):
            print u"Deprecated web.Auth en %s" % obj.path_info
            if obj.user is None:
                raise utils.AuthUserException("User is None!")
            
            conds = self._conditions
            if conds is None:
                if hasattr(obj, "conditions"):
                    conds = getattr(obj, "conditions")
            if not isinstance(conds, list):
                conds = []
            
            if not utils.check_conditions(obj.user, conds):
                raise utils.AuthConditionException("Condition failed")
            
            return func(obj, *args, **kwargs)
        
        return wrapper

#-----------------------------------------------------------------------------------------

class Template(AbstractDecorator):
    """ Decorator for content rendering using template
        The instance with de decorated method must have a 'path_info' attribute
        Templates for 'login' and 'role_error' requiered for user auth.
    """
    
    def __init__(self, uri=None, exposed=True, **kwa):
        AbstractDecorator.__init__(self)
        self._uri = uri
        self._exposed = exposed
        self._kwa = kwa
    
    def getWrapper(self, func):
        def wrapper(obj, *args, **kwargs):
            print u"Deprecated web.Template en %s" % obj.path_info
            try:
                result = func(obj, *args, **kwargs)
                result = result if isinstance(result, dict) else {}
                result.update(self._kwa)
                uri = obj.path_info if (self._uri is None) else self._uri
                return utils.lookup.render(uri, **result)
            except utils.AuthUserException:
                return utils.lookup.render("login", page=obj)
            except utils.AuthConditionException:
                return utils.lookup.render("role_error", page=obj)
            except Exception, e:
                print e
        
        wrapper.exposed = self._exposed
        return wrapper

#-----------------------------------------------------------------------------------------

class ExposeOld(AbstractDecorator):
    """ Decorator for exposing content and optional rendering using template
        The instance with de decorated method must have a 'path_info' attribute if
        a template is needed.
        Templates for 'login' and 'role_error' requiered for user auth.
    """
    
    def __init__(self, uri=None, verbs=["GET"], **kwa):
        AbstractDecorator.__init__(self)
        self._uri = uri
        self._kwa = kwa
        self._verbs = verbs
    
    def getWrapper(self, func):
        def wrapper(obj, *args, **kwargs):
            print u"Deprecated web.ExposeOld en %s" % obj.path_info
            if not(cherrypy.request.method in self._verbs):
                print u"%s Error de método: %s" % (obj.path_info, cherrypy.request.method)
                return utils.lookup.render("basic_error", page=obj)
            try:
                result = func(obj, *args, **kwargs)
                if not isinstance(result, dict):
                    return result
                result.update(self._kwa)
                uri = obj.path_info if (self._uri is None) else self._uri
                return utils.lookup.render(uri, **result)
            except utils.AuthUserException:
                return utils.lookup.render("login", page=obj)
            except utils.AuthConditionException:
                return utils.lookup.render("role_error", page=obj)
            except Exception, e:
                print u"%s Error: %s" % (obj.path_info, e)
                return utils.lookup.render("basic_error", page=obj)
        
        wrapper.exposed = True
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

#-----------------------------------------------------------------------------------------

class FxExpose(AbstractDecorator):
    """ Decorator for exposing content, optional authentication.
        The instance with de decorated method must have:
        - Attributes: user and path_info
    """
    
    def __init__(self, verbs="GET", auth=None):
        AbstractDecorator.__init__(self)
        
        self._verbs = [x.strip().upper() for x in verbs.split(",")]
        
        self._authreq = False if (auth is None) else True
        self._conds = []
        
        if self._authreq:
            if isinstance(auth, list):
                self._conds = auth
            else:
                self._conds.append(auth)
    
    def getWrapper(self, func):
        def wrapper(obj, *args, **kwargs):
            
            # verbs check
            if not(cherrypy.request.method in self._verbs):
                print u"%s Error de método: %s" % (obj.path_info, cherrypy.request.method)
                return utils.tojson(dict(status=False, error="verb"))
            
            # auth check
            if self._authreq:
                if obj.user is None:
                    return utils.tojson(dict(status=False, error="login"))
                
                if not utils.check_conditions(obj.user, self._conds):
                    return utils.tojson(dict(status=False, error="role"))
            
            try:
                result = func(obj, *args, **kwargs)
                return result
            except Exception, e:
                print u"%s Error: %s" % (obj.path_info, e)
                return utils.tojson(dict(status=False, error="method"))
        
        wrapper.exposed = True
        return wrapper
