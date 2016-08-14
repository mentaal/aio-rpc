from .AioJsonClient import AioJsonClient
from asyncio import Future
from functools import partial
class ClientObj():
    '''Proxy object for object being served. User will attempt attribute access
    on this object'''

    def __init__(self, event_loop, q):
        '''safe event_loop and queue objects'''
        self._event_loop = event_loop
        self._q = q
        self._future_dict = {}
        self._json_client = AioJsonClient(
                event_loop=self._event_loop,
                future_dict=self.future_dict)


    def __getattr__(self, item):
        #return self._funcs[item] #implicitly raise an KeyError if not found

        p = partial(self._caller, item)

        return p


    async def _caller(self, __method, *args, **kwargs):
        '''this function is effectively being called by user'''
        request_json, id_num = self._json_client.request(
                __method,
                positional_params=args,
                keyword_params = kwargs)
        #issue it for dispatch
        self._q.put_nowait(request_json)

        #now create a future to wait on
        f = Future(loop=self._event_loop)

        #store it in the request_dict to AioJsonClient can set its result.
        self._future_dict[id_num] = f

        #now await for the result
        return await f


