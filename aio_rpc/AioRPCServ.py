import asyncio
import time
import aiohttp
from aiohttp import web
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import setup, get_session, SimpleCookieStorage
from .AioJsonSrv import AioJsonSrv
from .Wrapper import Wrapper
import ssl
import logging

logger = logging.getLogger(__name__)


class AioRPCServ():
    '''The Server class which will serv up an object using RPC and
    WebSockets.'''

    def __init__(self, class_to_instantiate, timeout):
        '''
        Args:
            class_to_instantiate (class): the class of the object to instantiate
            timeout (int): The time after which an exception is raised if the
            method being served doesn't complete
        '''

        event_loop = asyncio.get_event_loop()

        obj = Wrapper(cls=class_to_instantiate, cls_args=None, loop=event_loop,
                timeout = timeout)
        self.json_srv = AioJsonSrv(obj=obj)

        self.event_loop = event_loop
        self.locked = False

    async def get_access(self, request):
        session = await get_session(request)
        if self.locked:
            logger.debug("resource is already locked...")
            session['resource_granted']= 'False'
            message = 'Sorry resource is busy, try again in a while...'
        else:
            self.locked = True
            logger.debug("locking device..")
            message = 'Resource granted'
            session['resource_granted'] = 'True'
        return web.Response(body=message.encode('utf-8'))




    async def root_handler(self, request):
        session = await get_session(request)
        last_visit = session.get('last_visit', 'Never')
        if last_visit == 'Never':
            message = "Welcome, I don't think you've visited here before."
        else:
            message = 'Welcome back, last visited: {} secs ago'.format(time.time() -
                    last_visit)
        session['last_visit'] = time.time()
        session['authenticated'] = 'True'

        return web.Response(body=message.encode('utf-8'))

    async def ws_handler(self, request):

        session = await get_session(request)
        ws = web.WebSocketResponse()
        await ws.prepare(request)


        granted = session.get('resource_granted', None)
        logger.debug("granted: {} type(granted): {}".format(granted, type(granted)))

        _granted = False

        if granted is not None and granted == 'True':
            _granted = True
            logger.debug("user is granted..")


        if not _granted:
            await ws.close()
            logger.debug("not granted...returning")
            return
            #await ws.close(code=999, message='Resource busy'.encode('utf-8'))
            #await ws.close(code=999, message='Resource busy'.encode('utf-8'))



        async for msg in ws:
            logger.debug("received msg: {}".format(msg.data))
            if msg.tp == aiohttp.MsgType.text:
                #if msg.data == 'close':
                #    await ws.close()
                #else:
                result_json, error = await self.json_srv.process_incoming(msg.data)
                ws.send_str(result_json)
            elif msg.tp == aiohttp.MsgType.error:
                logger.debug('ws connection closed with exception %s' % ws.exception())

        if self.locked:
            logger.debug("Unlocking device..")
            self.locked = False
        logger.debug('websocket connection closed')

        return ws

    def run(self):
        sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslcontext.load_cert_chain('cert.pem')
        event_loop = self.event_loop
        app = web.Application(loop=event_loop)
        #setup(app, SimpleCookieStorage())
        setup(app, EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))
        app.router.add_route('GET', '/', self.root_handler)
        app.router.add_route('GET', '/wss', self.ws_handler)
        app.router.add_route('GET', '/get_access', self.get_access)
        web.run_app(app, host='0.0.0.0', port=8080, ssl_context=sslcontext)
