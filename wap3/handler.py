# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ
try:
    import simplejson as json
except ImportError:
    import json
import cherrypy
from utils import lookup, FMT_RAW, FMT_TPL, FMT_JSON, FMT_JSONTPL

#-----------------------------------------------------------------------------------------

__all__ = ['Handler']

#-----------------------------------------------------------------------------------------

class Handler(object):
    """ Abstract base class for request handlers
        Si se usa con GAE sessions requiere la siguiente configuración:
        
        APP_CONF = {
            "/": {
                "tools.sessions.on": True,
                "tools.sessions.clean_freq": 0,
                "tools.sessions.persistent": False,
            },
        }
        
    """
    
    redirect = cherrypy.HTTPRedirect
    httperror = cherrypy.HTTPError
    
    #-------------------------------------------------------------------------------------
    
    def _getRequest(self):
        return cherrypy.request
    request = property(_getRequest)
    
    def _getResponse(self):
        return cherrypy.response
    response = property(_getResponse)
    
    #-------------------------------------------------------------------------------------
    # Métodos para registro de valores en la session actual
    
    def setSession(self, key, value):
        # Graba información de sessión global
        cherrypy.session[key] = value
    
    def getSession(self, key, default=None):
        # Recupera información de sessión global
        return cherrypy.session.get(key, default)
    
    #-------------------------------------------------------------------------------------
    # Métodos para verificación y registro de usuarios
    
    def checkUser(self):
        """Must return True if a valid user is logedin, False otherwise.
           Can be overwritted for special user requirements.
        """
        return not (self.user is None)
    
    def checkAuth(self, conditions):
        """Check if self.user fullfill the auth conditions.
           Return True if all pass and False if at least one fails.
           User and conditions must be implemented by developers
        """
        for func in conditions:
            if not func(self.user):
                return False
        return True
    
    def getUser(self):
        """Must return the current user, None or raise AttributeError
        """
        raise AttributeError("can't get attribute 'user'")
    
    def _getUser(self):
        return self.getUser()
    
    def setUser(self, user):
        """Must set the current or raise AttributeError
        """
        raise AttributeError("can't set attribute 'user'")
    
    def _setUser(self, user):
        self.setUser(user)
    
    user = property(_getUser, _setUser)
    
    #-------------------------------------------------------------------------------------
    # Métodos llamados por expose decorators para enviar errores
    
    def error(self, err, fmt, **kwa):
        if fmt == FMT_RAW:
            return self.errorRaw(err)
        if fmt == FMT_TPL:
            return self.errorTemplate(err)
        if fmt == FMT_JSON:
            return self.errorJson(err)
        if fmt == FMT_JSONTPL:
            return self.errorRaw(err, **kwa)
    
    def errorRaw(self, err):
        msg = u"ERROR: %s" % err
        raise self.httperror(403, msg.encode("utf-8"))
       
    def errorTemplate(self, err):
        return lookup.render("/error_basic", handler=self, err=err)
    
    def errorJson(self, err):
        return json.dumps(dict(ok=False, err=err))
    
    def errorJsonTemplate(self, err, **kw):
        data = u"ERROR: %s" % err
        inline = kw.get("inline", False)
        
        if inline is False:
            data = lookup.render("/error_basic_json", err=err)
        
        sal = dict(ok=False, err=err, data=data)
        return json.dumps(sal)
    
    #-------------------------------------------------------------------------------------
    # Métodos llamados por expose decorators para enviar respuestas
    
    def render(self, fout, uri, fmt, **kwa):
        if fmt == FMT_RAW:
            return self.renderRaw(fout)
        if fmt == FMT_TPL:
            return self.renderTemplate(fout, uri, **kwa)
        if fmt == FMT_JSON:
            return self.renderJson(fout, **kwa)
        if fmt == FMT_JSONTPL:
            return self.renderJsonTemplate(fout, uri, **kwa)
    
    def renderRaw(self, fout):
        return fout
    
    def renderTemplate(self, fout, uri, **kwa):
        fout.update(kwa)
        return lookup.render(uri, **fout)
    
    def renderJson(self, fout, **kwa):
        fout.update(kwa)
        return json.dumps(fout)
    
    def renderJsonTemplate(self, fout, uri, **kwa):
        fout.update(kwa)
        sal = dict(ok=True, err="", data=lookup.render(uri, **fout))
        return json.dumps(sal)