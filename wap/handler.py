# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import os, json
import cherrypy

#-----------------------------------------------------------------------------------------

__all__ = ['ERROR_LOGIN', 'ERROR_ROLES', 'ERROR_VERBS', 'ERROR_METHOD',
           'FMT_RAW', 'FMT_TPL', 'FMT_JSON', 'FMT_JSONTPL',
           'Handler']

#-----------------------------------------------------------------------------------------
# Constantes del módulo

# Valores de Error
ERROR_LOGIN  = u"LOGIN"
ERROR_ROLES  = u"ROLES"
ERROR_VERBS  = u"VERBS"
ERROR_METHOD = u"METHOD"    # Error informed by method (not sended by expose classes)

# Valores de formato de salida
FMT_RAW     = u"RAW"
FMT_TPL     = u"TPL"
FMT_JSON    = u"JSON"
FMT_JSONTPL = u"JSONTPL"

#-----------------------------------------------------------------------------------------

class Handler(object):
    """ Abstract base class for request handlers
        
        Clases derivadas deben definir los siguientes atributos de clase:
        lookup: TemplateLookup (por el momento solo MakoLookup)
    """
    
    def __init__(self):
        if not hasattr(self, "lookup"):
            raise Exception("Class attribute 'lookup' requiered!")
    
    #-------------------------------------------------------------------------------------
    # Métodos de acceso a cherrypy
    
    redirect = cherrypy.HTTPRedirect
    httperror = cherrypy.HTTPError
    
    def _getRequest(self):
        return cherrypy.request
    request = property(_getRequest)
    
    def _getResponse(self):
        return cherrypy.response
    response = property(_getResponse)
    
    def _getSession(self):
        return cherrypy.session
    session = property(_getSession)
    
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
    
    def error(self, fmt, err):
        if fmt == FMT_TPL:
            return self.errorTemplate(err)
        if fmt == FMT_JSON:
            return self.errorJson(err)
        if fmt == FMT_JSONTPL:
            return self.errorJsonTemplate(err)
        return self.errorRaw(err)
    
    def errorRaw(self, err):
        msg = u"ERROR: %s" % err
        raise self.httperror(403, msg.encode("utf-8"))
    
    def errorTemplate(self, err):
        return self.lookup.render("/error_basic", handler=self, err=err)
    
    def errorJson(self, err):
        return json.dumps(dict(ok=False, err=err))
    
    def errorJsonTemplate(self, err):
        data = self.lookup.render("/error_basic_json", err=err)
        sal = dict(ok=False, err=err, data=data)
        return json.dumps(sal)
    
    #-------------------------------------------------------------------------------------
    # Métodos llamados por expose decorators para enviar respuestas
    
    def send(self, fmt, uri, fout):
        if fmt == FMT_TPL:
            return self.sendTemplate(uri, fout)
        if fmt == FMT_JSON:
            return self.sendJson(fout)
        if fmt == FMT_JSONTPL:
            return self.sendJsonTemplate(uri, fout)
        return self.sendRaw(fout)
    
    def sendRaw(self, fout):
        return fout
    
    def sendTemplate(self, uri, fout):
        return self.lookup.render(uri, **fout)
    
    def sendJson(self, fout):
        return json.dumps(fout)
    
    def sendJsonTemplate(self, uri, fout):
        sal = dict(ok=True, err="", data=self.lookup.render(uri, **fout))
        return json.dumps(sal)