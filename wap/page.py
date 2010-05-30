# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy

#-----------------------------------------------------------------------------------------

__all__ = ['Page']

#-----------------------------------------------------------------------------------------

class Page(object):
    """ Abstract base class for page handlers
    """
    
    redirect = cherrypy.HTTPRedirect
    httperror = cherrypy.HTTPError
    
    def __init__(self, url="/"):
        self.url = url
    
    def _getRequest(self):
        return cherrypy.request
    request = property(_getRequest)    
    
    def _getResponse(self):
        return cherrypy.response
    response = property(_getResponse)
    
    #-------------------------------------------------------------------------------------
    
    def checkUser(self, conditions):
        """Check if self.user fullfill the conditions.
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
