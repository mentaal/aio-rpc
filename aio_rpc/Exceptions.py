class JsonRPCError(Exception):
    '''This Exception forms the ABC for the errors as defined within the
JSON-RPC 2.0 specification. It is not intended to be instantiated directly '''

    code    = -32000
    error   = 'Unspecified Error'
    message = ''

    def __str__(self):
        return 'Error code: {} - {} - {}'.format(self.code,
                                                   self.error,
                                                   self.__doc__)
    def json_format(self):
        return {
                   'code'   : self.code,
                   'message': self.error,
                   'data'   : '\n'.join((self.__doc__, self.message))
               }

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

