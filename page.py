# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import cherrypy
import utils

#-----------------------------------------------------------------------------------------

__all__ = ['Page']

#-----------------------------------------------------------------------------------------

SESSION_GLOBAL_USER_KEY = "_global_session_user"

class Page(object):
    """ Abstract base class for page handlers
        Optional in derived classes: conditions
    """
    
    def __init__(self, url="/"):
        self.url = url
    
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
        whe = " and ".join([x.strip() for x in where.split(",")])
        whe = ("where " + whe) if whe != "" else ""
        oby = ("order by " + orderby) if orderby != "" else ""
        query = "select %s from %s %s %s" % (sel, tables, whe, oby)
        return self.fetch(query, params)
    
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
    
    def setUser(self, user):
        cherrypy.session[SESSION_GLOBAL_USER_KEY] = user
    
    def getUser(self):
        return cherrypy.session.get(SESSION_GLOBAL_USER_KEY, None)
    
    user = property(getUser, setUser)