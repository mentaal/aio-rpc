import json
from .Exceptions import UnimplementedError
from aio_rpc.Exceptions import (
        ParseError,
        InvalidRequestError,
        NotFoundError,
        InvalidParamsError,
        InternalError,
        UnimplementedError)

class JsonRPCABC():
    '''Abstract Base Class defining generic functions relating to JSON-RPC 2.0.
    The referenced specification is available here:
    http://www.jsonrpc.org/specification.'''

    _id = 0

    def request(self, method_name:str, *, id_num=None, positional_params=None,
            keyword_params:dict=None, notification=False):
        '''create a json request object out of the specified arguments
        provided.'''

        request_dict = {
                'jsonrpc' : '2.0',
                'method'  : method_name}

        id_to_use = None
        if not notification:
            if id_num is not None:
                id_to_use = id_num
            else:
                id_to_use = self._id
                self._id += 1
            request_dict['id'] = id_to_use

        #grab the first non empty argument and default to None otherwise
        params_to_use = next(
            (_ for _ in (positional_params, keyword_params) if _), None)

        if params_to_use:
            request_dict['params'] = params_to_use

        return json.dumps(request_dict)

    def response_result(self, id_num:int, result):
        '''create an result response object based on the given arguments
        Args:
            id_num (int): the id of the response
            result : some form of object that is parsable into json format

        Returns:
            str: A json formatted string'''

        response_dict = {
                'jsonrpc' : '2.0',
                'result'  : result,
                'id'      : id_num
                        }
        return json.dumps(response_dict)

    def response_error(self, exception):
        '''create an error response object based on the given arguments
        Args:
            exception (JsonRPCError): an exception with the necessary
            information to generate a JSON error response object

        Returns:
            str: A json formatted string'''

        response_dict = {
                'jsonrpc' : '2.0',
                'error'   : exception.to_json_rpc_dict(),
                'id'      : 'Null'
                        }
        return json.dumps(response_dict)

    def process_request(self, request):
        '''Received JSON indicates a request object. A server would need to
        cater for this function. A client wouldn't need to implement this.
        There is a possibility that an implementation of this class could
        operate as a peer in which case it would make sense to implement this
        function when implementing a client.

        Args:
            request (dict): a dictionary containing the request to service'''

        raise UnimplementedError()

    def process_response(self, response):
        '''Received JSON indicates a response object. A server would not need to
        cater for this function. A client would need to implement this.
        There is a possibility that an implementation of this class could
        operate as a peer in which case it would make sense to implement this
        function when implementing a server'''

        raise UnimplementedError()

    def process_incoming(self, json_obj:str) -> str:
        '''Process an incoming (either to a client or server) string. This
        function is always expected to return some form of string which can be
        sent to the sender in a jsonified string.'''

        try:
            result = json.loads(json_obj)
        except ValueError as e:
            p = ParseError()
            p.details = e.__str__()
            return self.response_error(p)



class JsonRPCClient(JsonRPCABC):
    pass

class JsonRPCServer(JsonRPCABC):
    pass
