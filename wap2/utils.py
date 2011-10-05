# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import os
from mako.lookup import TemplateLookup

#-----------------------------------------------------------------------------------------

__all__ = ['ERROR_LOGIN', 'ERROR_ROLES', 'ERROR_VERBS', 'ERROR_METHOD',
           'FMT_RAW', 'FMT_TPL', 'FMT_JSON', 'FMT_JSONTPL',
           'lookup']

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

class MakoLookup(object):

    def __init__(self):
        self._lookup = None
        self._defaultext = None
    
    def config(self, directory, defaultext="tpl", input_encoding='utf-8', output_encoding='utf-8',
               encoding_errors='replace'):
        
        self._defaultext = defaultext
        
        self._lookup = TemplateLookup(directories=[directory],
            #module_directory='./tmp',    # No se puede usar en GAE
            input_encoding=input_encoding,
            output_encoding=output_encoding,
            encoding_errors=encoding_errors
        )
    
    def getUri(self, uri):
        if uri.endswith("/"):
            uri = uri + "index" 
        
        if self._defaultext is None:
            return uri
        
        root, ext = os.path.splitext(uri)
        if ext == "":
            return "%s.%s" % (uri, self._defaultext)
        if ext==".":
            return root
        return uri
    
    def render(self, uri, **kwa):
        """ Function for templates renderign
        """
        if self._lookup is None:
            raise Exception("Lookup is not configured!")
        
        uri = self.getUri(uri)
        tpl = self._lookup.get_template(uri)
        txt = tpl.render(**kwa)
        return txt

#-----------------------------------------------------------------------------------------
# lookup: _MakoLookup instance

lookup = MakoLookup()
