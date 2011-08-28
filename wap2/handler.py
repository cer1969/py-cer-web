# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ
try:
    import simplejson as json
except ImportError:
    import json
import cherrypy
from utils import lookup
from expose import ERROR_LOGIN, ERROR_ROLES, ERROR_VERBS

#-----------------------------------------------------------------------------------------

__all__ = ['Handler', 'MSGS']

#-----------------------------------------------------------------------------------------

MSGS = {
    ERROR_LOGIN: u"INICIO DE SESIÓN REQUERIDO",
    ERROR_ROLES: u"NO TIENE PRIVILEGIOS SUFICIENTES",
    ERROR_VERBS: u"ERROR DE ACCESO"
}

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
    # Métodos llamados por expose decorators para enviar respuestas y errores
    
    def errorRaw(self, err):
        txt = u"%s: %s" % (err, MSGS[err])
        raise self.httperror(403, txt.encode("utf-8"))
    
    def renderRaw(self, fout):
        return fout
    
    def errorTemplate(self, err):
        return lookup.render("/error_basic", err=err, msg=MSGS[err])
    
    def renderTemplate(self, fout, uri, **kwa):
        fout.update(kwa)
        return lookup.render(uri, **fout)
    
    def errorJson(self, err):
        sal = dict(ok=False, err=err, msg=MSGS[err])
        return json.dumps(sal)
    
    def renderJson(self, fout, **kwa):
        fout.update(kwa)
        fout.update(ok=True, err="")
        return json.dumps(fout)
    
    def errorJsonTemplate(self, err, inline):
        data = u"[ERROR: %s]" % err
        if inline is False:
            data=lookup.render("/error_basic_json", err=err, msg=MSGS[err])
        
        sal = dict(ok=False, err=err, msg=MSGS[err], data=data)
        return json.dumps(sal)
    
    def renderJsonTemplate(self, fout, uri, **kwa):
        fout.update(kwa)
        sal = dict(ok=True, err="", msg="", data=lookup.render(uri, **fout))
        return json.dumps(sal)
