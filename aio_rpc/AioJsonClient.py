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
import asyncio

logger = logging.getLogger(__name__)


class AioJsonClient(JsonRPCABC):
    '''Implementation of client side RPC'''

    def __init__(self, event_loop, future_dict):
        '''takes an event loop argument on which to schedule futures

        Args:
            event_loop (asyncio event loop): used to schedule coroutines
            future_dict (dict): used to hold a dictionary of existing futures
            to match incoming responses to.
            future_dict has records in the form:
            req_id: (request_json, request_future)'''

        self.loop = event_loop
        self.future_dict = future_dict

    async def process_incoming(self, json_obj:str):
        '''subclass to raise an exception if result is an error'''
        response, exception = await super().process_incoming(json_obj)
        #exception will be raised at the caller via the future
        #this should probably still be here in case the future id is not found
        if exception:
            raise exception
        return response

    def process_error(self, result:dict):
        id_num = result.get('id', None)
        if id_num is not None:
            f = self.future_dict.pop(id_num)
            exc = self.exception_from_json_dict(result['error'])
            f.set_exception(exc)
            return None, None
        else:
            exc = self.exception_from_json_dict(result['error'])
            return None, exc


    def process_response(self, response):
        '''correlate response with stored requests/futures and set result on
        future accordingly'''
        id_num = response['id']
        if id_num in self.future_dict:
            request_future = self.future_dict[id_num]
            request_future.set_result(response['result'])
        else:
            raise(InternalError('Received RPC response with an invalid ID'))

        return response, None #not much use for this just yet


