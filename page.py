# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy

#-----------------------------------------------------------------------------------------

__all__ = ['Page']

#-----------------------------------------------------------------------------------------

SESSION_GLOBAL_USER = "_session_global_user"

class Page(object):
    """ Abstract base class for page handlers
    """
    
    def __init__(self, url="/"):
        self.url = url
    
    def _getPathInfo(self):
        return cherrypy.request.path_info
    
    path_info = property(_getPathInfo)
    
    def _setUser(self, user):
        # Set current user
        self.setSession(SESSION_GLOBAL_USER, user)
    
    def _getUser(self):
        # Get current user
        return self.getSession(SESSION_GLOBAL_USER)
    
    user = property(_getUser, _setUser)
    
    def _getDb(self):
        return cherrypy.thread_data.db
    
    db = property(_getDb)
    
    #-------------------------------------------------------------------------------------
    # Cookies and Sessions
    
    def getCookie(self, name, default=None):
        cook = cherrypy.request.cookie.get(name)
        value = default if (cook is None) else cook.value
        return value
    
    def setCookie(self, name, value, maxage=None, url=None):
        cook = cherrypy.response.cookie
        cook[name] = value
        if maxage:
            cook[name]['max-age'] = maxage
        url = self.url if (url is None) else url
        cook[name]['path'] = url
    
    def setSession(self, key, value):
        # Graba información de sessión global
        cherrypy.session[key] = value
    
    def getSession(self, key, default=None):
        # Recupera información de sessión global
        return cherrypy.session.get(key, default)
    
    def setPageData(self, key, value):
        # Graba información de sessión asociada a esta página
        gs = self.getSession(self.url, {})
        gs[key] = value
        self.setSession(self.url, gs)
    
    def getPageData(self, key, default=None):
        # Recupera información de sessión asociada a esta página
        gs = self.getSession(self.url, {})
        return gs.get(key, default)