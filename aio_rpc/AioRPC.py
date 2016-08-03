import asyncio
import time
import inspect
from aiohttp import web
from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
# This restores the default Ctrl+C signal handler, which just kills the process
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import logging
import wrapt
from functools import partial

logger = logging.getLogger(__name__)

def func_caller(host_instance, timeout):
    '''Use wrapt module to decorate the functions which we shall call. This
    should hopefully aid with introspection of the functions which are
    available. 

    Args:
        host_instance (AioRPC instance): Using a closure here to provide a
        reference to AioRPC instance for loop and executor lookup

        timeout (int): A timeout after which an an execption will be raised

    Returns:
        method (AioRPC method): a wrapped method which gets executed using
        AioRPC executor
    '''

    @wrapt.decorator
    async def new_func(wrapped, instance, args, kwargs):
        p = partial(wrapped,*args, **kwargs)
        future = host_instance.loop.run_in_executor(host_instance.executor, p)
        logger.info("Calling function:{}".format(wrapped.__name__))
        return await asyncio.wait_for(future, timeout, loop=host_instance.loop)
    return new_func


class AioRPC():
    '''Class to expose an instantiated object via WS and JSON. It is assumed
    that the object is already instantiated. All methods of the class get
    exposed except those with prefixes of _ or __. Additionally a blacklist can
    be provided to prevent some methods from being exposed. A whitelist can
    alternatively be provided to only expose the specified functions '''

    def __init__(self, obj, loop, whitelist=None, blacklist=None,
            executor=ProcessPoolExecutor, timeout=5):
        '''Initialize what methods are exposed. Also intialize an executor to
        run the object's methods in. THis is because they could be blocking and
        calling these directly would drastically affect the reactivity of the
        event loop.

        Args:
            obj (object): The object to expose

            loop (asyncio event loop): The event loop to use when scheduling a
            function

        Kwargs:
            whitelist (iterable): A list of methods to expose
            blacklist (iterable): A list of methods not to expose
            timeout (int): The timeout value to wait for the executed functions
            to return
            executor (ProcessPoolExecutor or ThreadPoolExecutor): The executor
            upon which to execute the objects functions.

        Whitelist and blacklist of mutually exclusive. Only use one of
        these!

        >>> loop = asyncio.get_event_loop()
        >>> class t():
        ...     def func(self):
        ...         pass
        >>> a = AioRPC(t, loop, whitelist=['func'])

        '''

        self._obj = obj
        self.loop = loop

        self._create_executor(executor=ProcessPoolExecutor)

        obj_methods = inspect.getmembers(obj, inspect.ismethod)

        self.funcs = {}

        if whitelist is not None:
            for func_name,func in obj_methods:
                if func_name in whitelist:
                    self.funcs[func_name] = func_caller(self,timeout)(func)
        elif blacklist is not None:
            for func_name,func in obj_methods:
                if func_name in blacklist or func_name[0] == '_':
                    continue
                self.funcs[func_name] = func_caller(self,timeout)(func)
        else:
            for func_name,func in obj_methods:
                if func_name[0] == '_':
                    continue
                self.funcs[func_name] = func_caller(self,timeout)(func)



    def _create_executor(self, executor=ProcessPoolExecutor):
        '''Create an Executor. Default is to create a ProcessPoolExecutor.
        We only need one worker.'''
        self.executor = executor(max_workers=1)

