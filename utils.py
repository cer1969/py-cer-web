# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

from mako import exceptions
from mako.lookup import TemplateLookup
try:
    import simplejson as json
except ImportError:
    import json

#-----------------------------------------------------------------------------------------

__all__ = ['lookup', 'check_conditions', 'tojson']

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
            raise Exception("Lookup is not configured!")
        
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
# check conditions

def check_conditions(user, conditions):
    """user and conditions must be implemented by developers
    """
    for func in conditions:
        if not func(user):
            return False
    return True

#-----------------------------------------------------------------------------------------
# simplejson

def tojson(**kwargs):
    return json.dumps(kwargs)