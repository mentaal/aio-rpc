import asyncio
import time
import aiohttp
from aiohttp import web
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import setup, get_session, SimpleCookieStorage
from .AioJsonSrv import AioJsonSrv
from .Wrapper import Wrapper


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

        #print(session.get('last_visit'))

        ws = web.WebSocketResponse()

        await ws.prepare(request)


        async for msg in ws:
            print("received msg: {}".format(msg.data))
            if msg.tp == aiohttp.MsgType.text:
                if msg.data == 'close':
                    await ws.close()
                else:
                    result_json, error = await self.json_srv.process_incoming(msg.data)
                    ws.send_str(result_json)
            elif msg.tp == aiohttp.MsgType.error:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

    async def server_init(self, loop):
        app = web.Application()
        setup(app, SimpleCookieStorage())
        #setup(app, EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))
        app.router.add_route('GET', '/', self.root_handler)
        app.router.add_route('GET', '/ws', self.ws_handler)
        srv = await loop.create_server(
            app.make_handler(), '0.0.0.0', 8080)
        return srv

    def run(self):
        event_loop = self.event_loop
        srv = self.server_init(event_loop)

        event_loop.run_until_complete(srv)
        event_loop.run_forever()

