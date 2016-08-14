class JsonRPCError(Exception):
    '''This Exception forms the ABC for the errors as defined within the
JSON-RPC 2.0 specification. It is not intended to be instantiated directly '''

    code    = -32000
    error   = 'Unspecified Error'

    def __str__(self):
        return ' - '.join(
              filter(None, (str(self.code), self.error, super().__str__())))

    def to_json_rpc_dict(self):
        arg = super().__str__()
        #only add details (the argument to the exception) if it exists
        d =    {
                   'code'   : self.code,
                   'message': self.error,
                   'data'   : {a:b for a,b in
           (('explanation',self.__doc__),('details',arg)) if b }
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

exceptions_from_codes = {
        JsonRPCError.code : JsonRPCError,
        ParseError.code : ParseError,
        InvalidRequestError.code : InvalidRequestError,
        NotFoundError.code       : NotFoundError,
        InvalidParamsError.code  : InvalidParamsError,
        InternalError.code       : InternalError,
        UnimplementedError.code  : UnimplementedError }
