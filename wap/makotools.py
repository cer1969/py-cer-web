# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ

import os
from mako.lookup import TemplateLookup

#-----------------------------------------------------------------------------------------

__all__ = ['MakoLookup']

#-----------------------------------------------------------------------------------------

class MakoLookup(object):
    
    def __init__(self, directories, default_ext="tpl", module_directory=None, 
                 input_encoding='utf-8', output_encoding='utf-8', 
                 encoding_errors='replace'):
        
        self._default_ext = default_ext
        
        self._lookup = TemplateLookup(directories=directories,
            module_directory=module_directory,    # No se puede usar en GAE
            input_encoding=input_encoding,
            output_encoding=output_encoding,
            encoding_errors=encoding_errors
        )
    
    def getUri(self, uri):
        if uri.endswith("/"):
            uri = uri + "index" 
        
        if self._default_ext is None:
            return uri
        
        root, ext = os.path.splitext(uri)
        if ext == "":
            return "%s.%s" % (uri, self._default_ext)
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