# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy

#-----------------------------------------------------------------------------------------

__all__ = ['Page']

#-----------------------------------------------------------------------------------------

class Page(object):
    """ Abstract base class for page handlers
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
