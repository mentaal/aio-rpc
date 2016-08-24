import aiohttp
import asyncio
from .AioJsonClient import AioJsonClient
from .ClientObj import ClientObj
from .Exceptions import NotFoundError
from .AioRPCClient import AioRPCClient
from functools import partial
import threading
import signal
from time import sleep
#signal.signal(signal.SIGINT, signal.SIG_DFL)
import logging
logger = logging.getLogger(__name__)

def worker_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
    logger.debug("worker_thread: loop stopped..")
    #print("closing loop...")
    #loop.close()

async def cancel_tasks(loop):
    #print("stopping client")

    for task in asyncio.Task.all_tasks(loop=loop):
        if task == asyncio.Task.current_task(loop=loop):
            continue
        #print("killing task: {}".format(task))
        task.cancel()
        await asyncio.wait([task]) #wait for it to finish canceling
    loop.stop()
    #print("finished stopping client")

class AioRPCThreadedClient():
    '''instantiate RPC client in another thread'''

    def __init__(self, *,
        host_addr='0.0.0.0',
        port=8080,
        timeout=2,
        secure=True
            ):
        '''initialize threaded rpc client.
        Args:
            host_addr (str): the address to connect to
            port (int): the port number to connect to
            timeout (int):the time after which the client gives up connecting to
            the server
            secure (bool): To connect via https or http
        '''
        self.host_addr = host_addr
        self.port = port
        self.timeout = timeout
        self.secure = secure
        print('using secure: {}'.format(self.secure))
        self._start_client()

    def _start_client(self):
        client = AioRPCClient(
                host_addr=self.host_addr,
                port=self.port,
                timeout=self.timeout,
                secure=self.secure)
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
        #wait until loop has stopped
        for i in range(10):
            if not l.is_running():
                break
            sleep(0.1)
        else:
            raise Exception("Error closing event loop!")
        future.cancel()
        #print("finished _stop_client...")


    def _caller(self, method, *args, **kwargs):
        '''this function is effectively being called by user'''

        m = getattr(self._client_obj, method)(*args, *kwargs)
        future = asyncio.run_coroutine_threadsafe(m, self._event_loop)
        return future.result()

