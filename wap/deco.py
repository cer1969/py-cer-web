# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
import utils

#-----------------------------------------------------------------------------------------

__all__ = ['cpexpose', 'HTTPRedirect', 'HTTPError', 'AbstractDecorator', 'AbstractExpose',
           'Expose', 'JsonExpose']

#-----------------------------------------------------------------------------------------
# Alias de cherrypy

cpexpose = cherrypy.expose
HTTPRedirect = cherrypy.HTTPRedirect
HTTPError = cherrypy.HTTPError

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
    
    def verbsError(self, page):
        raise NotImplementedError("This is an abstract class")
    
    def loginError(self, page):
        raise NotImplementedError("This is an abstract class")
    
    def roleError(self, page):
        raise NotImplementedError("This is an abstract class")
    
    def getResult(self, page, data):
        raise NotImplementedError("This is an abstract class")
    
    def getWrapper(self, func):
        def wrapper(page, *args, **kwargs):
            
            # verbs check
            if not(cherrypy.request.method in self._verbs):
                return self.verbsError(page)
            
            # auth check
            if self._authreq:
                if page.user is None:
                    return self.loginError(page)
                if not utils.checkConditions(page.user, self._conds):
                    return self.roleError(page)
            
            return self.getResult(page, func(page, *args, **kwargs))
        
        wrapper.exposed = True
        return wrapper

#-----------------------------------------------------------------------------------------

class Expose(AbstractExpose):
    """ Decorator for exposing content, optional rendering using template and
        optional authentication.
        The instance with de decorated method must have:
        - Attributes: user and pathInfo
        - Templates: error_basic, error_login, error_role, error_post
    """
    
    def __init__(self, verbs="GET,POST", auth=None, uri=None, **kwa):
        AbstractExpose.__init__(self, verbs, auth)
        self._uri = uri
        self._kwa = kwa
    
    def _doErr(self, page, tpl, msg):
        if cherrypy.request.method == "GET":
            return utils.lookup.render(tpl, page=page)
        else:
            return utils.lookup.render("error_post", page=page, msg=msg)
    
    def verbsError(self, page):
        return self._doErr(page, "error_basic", u"ERROR DE ACCESO")
    
    def loginError(self, page):
        return self._doErr(page, "error_login", u"INICIO DE SESIÓN REQUERIDO")
    
    def roleError(self, page):
        return self._doErr(page, "error_role", u"NO TIENE PRIVILEGIOS SUFICIENTES")
    
    def getResult(self, page, data):
        if not isinstance(data, dict):
            return data
        data.update(self._kwa)
        uri = page.pathInfo if (self._uri is None) else self._uri
        return utils.lookup.render(uri, **data)


#-----------------------------------------------------------------------------------------

class JsonExpose(AbstractExpose):
    """ Decorator for exposing content returning json data with optional authentication.
        The instance with de decorated method must have:
        - Attributes: user and pathInfo
    """
    
    def _doErr(self, err, msg):
        return utils.toJson(json_ok=False, json_err=err, msg=msg)
    
    def verbsError(self, page):
        return self._doErr(u"VERBS", u"ERROR DE ACCESOs")
    
    def loginError(self, page):
        return self._doErr(u"LOGIN", u"INICIO DE SESIÓN REQUERIDO")
    
    def roleError(self, page):
        return self._doErr(u"ROLE", u"NO TIENE PRIVILEGIOS SUFICIENTES")
    
    def getResult(self, page, data):
        try:
            sal = dict(json_ok=True, json_err=u"")
            if isinstance(data, dict):
                sal.update(data)
            else:
                sal["json_data"] = data
            return utils.toJson(**sal)
        except Exception:
            return utils.toJson(json_ok=False, json_err=u"APP")