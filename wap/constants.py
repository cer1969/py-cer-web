# CRISTIAN ECHEVERRÍA RABÍ

__all__ = ['ERROR_LOGIN', 'ERROR_ROLES', 'ERROR_VERBS', 'ERROR_METHOD',
           'FMT_RAW', 'FMT_TPL', 'FMT_JSON', 'FMT_JSONTPL']

#-----------------------------------------------------------------------------------------
# Constantes del módulo

# Valores de Error
ERROR_LOGIN  = 401
ERROR_ROLES  = 403
ERROR_VERBS  = 405
ERROR_METHOD = 500  # Error informed by method (not sended by expose classes)

# Valores de formato de salida
FMT_RAW     = "RAW"
FMT_TPL     = "TPL"
FMT_JSON    = "JSON"
FMT_JSONTPL = "JSONTPL"