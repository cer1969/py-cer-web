# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

from mako import exceptions
from mako.lookup import TemplateLookup
import simplejson

#-----------------------------------------------------------------------------------------

__all__ = ['lookup', 'json', 'WebException', 'LookupException', 'AuthException', 
           'AuthUserException', 'AuthConditionException', 'record_factory']

#-----------------------------------------------------------------------------------------

def _get_uri(uri):
    if uri.endswith("/"):
        uri = uri + "index"
    return uri

#-----------------------------------------------------------------------------------------

class _MakoLookup(object):

    def __init__(self):
        self._lookup = None
    
    def config(self, directory, input_encoding='utf-8', output_encoding='utf-8',
               encoding_errors='replace'):
        
        self._lookup = TemplateLookup(directories=[directory],
            #module_directory='./tmp',
            input_encoding=input_encoding,
            output_encoding=output_encoding,
            encoding_errors=encoding_errors
        )

    def render(self, uri, **kwa):
        """ Function for templates renderign
        """
        if self._lookup is None:
            raise LookupException("Lookup is not configured!")
        
        uri = _get_uri(uri) + ".tpl"
        
        try:
            tpl = self._lookup.get_template(uri)
            txt = tpl.render(**kwa)
        except:
            print exceptions.text_error_template().render()
            txt = "<h1>Render Error</h1>"
        return txt

#-----------------------------------------------------------------------------------------
# lookup: _MakoLookup instance

lookup = _MakoLookup()

#-----------------------------------------------------------------------------------------
# simplejson

def json(**kwargs):
    return simplejson.dumps(kwargs)

#-----------------------------------------------------------------------------------------
# Record factory for sqlite3

class _Record(dict):
    def __init__(self, names, values):
        dict.__init__(self, zip(names, values))
    def __getattr__(self, name):
        return self[name]

def record_factory(cursor, row):
    names = [x[0] for x in cursor.description]
    return _Record(names, row)

#-----------------------------------------------------------------------------------------
# Exceptions

class WebException(Exception):
    """ Standard exception for cerweb """
    pass

class LookupException(WebException):
    """ Exception for lookup """
    pass

class AuthException(WebException):
    """ Authentication Exception """
    pass

class AuthUserException(AuthException):
    """ User Authentication Exception """
    pass

class AuthConditionException(AuthException):
    """ Condition Authentication Exception """
    pass
