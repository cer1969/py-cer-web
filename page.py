# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
import utils

#-----------------------------------------------------------------------------------------

__all__ = ['Page']

#-----------------------------------------------------------------------------------------

SESSION_GLOBAL_USER = "_session_global_user"

class Page(object):
    """ Abstract base class for page handlers
        Optional in derived classes: conditions
    """
    
    def __init__(self, url="/"):
        self.url = url
    
    #-------------------------------------------------------------------------------------
    # Cherrypy Methods
    
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
    
    def getPathInfo(self):
        return cherrypy.request.path_info
    
    path_info = property(getPathInfo)
    
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
    
    def setUser(self, user):
        self.setSession(SESSION_GLOBAL_USER, user)
    
    def getUser(self):
        return self.getSession(SESSION_GLOBAL_USER)
    
    user = property(getUser, setUser)
    
    #-------------------------------------------------------------------------------------
    # Database Methods
    
    def execute(self, query, parameters=[]):
        db = cherrypy.thread_data.db
        cur = db.cursor()
        cur.execute(query, parameters)
        return cur.lastrowid

    def commit(self):
        db = cherrypy.thread_data.db
        db.commit()
        
    def fetch(self, query, parameters=[]):
        db = cherrypy.thread_data.db
        cur = db.cursor()
        cur.execute(query, parameters)
        return cur.fetchall()
    
    def select(self, tables, where="", params=[], orderby=""):
        sel = ", ".join([x.strip() + ".*" for x in tables.split(",")]) 
        whe = ("where " + where) if where != "" else ""
        oby = ("order by " + orderby) if orderby != "" else ""
        query = "select %s from %s %s %s" % (sel, tables, whe, oby)
        return self.fetch(query, params)