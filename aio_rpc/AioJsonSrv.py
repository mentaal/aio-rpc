from functools import partial
from .JsonRPCABC import JsonRPCABC
from .Exceptions import (
        ParseError,
        InvalidRequestError,
        NotFoundError,
        InvalidParamsError,
        InternalError,
        UnimplementedError)
import logging
import json

logger = logging.getLogger(__name__)


class AioJsonSrv(JsonRPCABC):
    '''Implementation of server side serving up an instance of Wrapper'''

    def __init__(self, *, obj):
        '''Initialize the Json RPC wrapper

        Args:
            obj (object): The object to expose
        '''
        self.obj = obj

    async def process_request(self, request):

        method_name = request['method']
        id_num = request['id']

        try:
            method = getattr(self.obj, method_name)
        except AttributeError as e:
            r = NotFoundError(e.__str__())
            return self.response_error(r, id_num=request['id']), r


        params = request.get('params', None)
        if params:
            if type(params) == list:
                p      = partial(method, *params)
                p_test = partial(self.obj._func_sigs[method_name].bind, *params)
            else:
                p      = partial(method, **params)
                p_test = partial(self.obj._func_sigs[method_name].bind, **params)
        else:
                p      = method
                p_test = self.obj._func_sigs[method_name].bind

        try:
            p_test()
        except TypeError as e:
            r = InvalidParamsError(e.__str__())
            return self.response_error(r, id_num=request['id']), r

        try:
            result = await p()
            result_prepared = self.response_result(id_num=id_num, result=result)
            return result_prepared, None

        except Exception as e:
            r = InternalError(e.__str__())
            return self.response_error(r, id_num=request['id']), r
            logger.error(e)

