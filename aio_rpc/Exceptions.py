class JsonRPCError(Exception):
    '''This Exception forms the ABC for the errors as defined within the
JSON-RPC 2.0 specification. It is not intended to be instantiated directly '''

    code    = -32000
    error   = 'Unspecified Error'
    details = None

    def __str__(self):
        return ' - '.join(
              filter(None, (str(self.code), self.error, super().__str__())))

    def to_json_rpc_dict(self):
        d =    {
                   'code'   : self.code,
                   'message': self.error,
               }
        if self.details is not None:
            d['data'] = {
                 'details'     : self.details,
                 'explanation' : self.__doc__
                        }
        return d


class ParseError(JsonRPCError):
    '''Invalid JSON was received by the server.'''
    '''An error occurred on the server while parsing the JSON text.'''
    code    = -32700
    error   = 'Parse Error'

class InvalidRequestError(JsonRPCError):
    'The JSON sent is not a valid Request object.'
    code    = -32600
    error   = 'Invalid Request'

class NotFoundError(JsonRPCError):
    'The method does not exist / is not available.'
    code    = -32601
    error   = 'Method not found'

class InvalidParamsError(JsonRPCError):
    'Invalid method parameter(s).'
    code    = -32602
    error   = 'Invalid params'

class InternalError(JsonRPCError):
    'Internal JSON-RPC error.'
    code    = -32603
    error   = 'Internal error'

class UnimplementedError(JsonRPCError):
    'Method is not implemented.'
    code    = -32000
    error   = 'Unimplemented error'
