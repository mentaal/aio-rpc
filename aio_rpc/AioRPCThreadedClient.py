import aiohttp
import asyncio
from .AioJsonClient import AioJsonClient
from .ClientObj import ClientObj
from .Exceptions import NotFoundError
from .AioRPCClient import AioRPCClient
from functools import partial
import threading
import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)

def worker_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
    #print("loop stopped..")
    #print("closing loop...")
    #loop.close()

async def cancel_tasks(loop):
    #print("stopping client")

    for task in asyncio.Task.all_tasks(loop=loop):
        if task == asyncio.Task.current_task(loop=loop):
            continue
        #print("killing task: {}".format(task))
        task.cancel()
    loop.stop()
    #print("finished stopping client")

class AioRPCThreadedClient():
    '''instantiate RPC client in another thread'''

    def __init__(self):
        self.start_client()

    def start_client(self):
        client = AioRPCClient()
        self._event_loop = client.event_loop
        #if self.event_loop.is_running():
        #    self.event_loop.stop()
        self._thread = threading.Thread(
            target=worker_thread, args=(self._event_loop,))
        self._thread.start()
        self._client_obj = client.client_obj

    def __getattr__(self, item):
        p = partial(self._caller, item)
        return p

    def _stop_client(self):
        l = self._event_loop
        future = asyncio.run_coroutine_threadsafe(cancel_tasks(l), l)


    def _caller(self, method, *args, **kwargs):
        '''this function is effectively being called by user'''

        m = getattr(self._client_obj, method)(*args, *kwargs)
        future = asyncio.run_coroutine_threadsafe(m, self._event_loop)
        return future.result()

