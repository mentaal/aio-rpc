import asyncio
import time
import aiohttp
from aiohttp import web
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import setup, get_session, SimpleCookieStorage


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

async def handler(request):
    session = await get_session(request)
    last_visit = session.get('last_visit', 'Never')
    if last_visit == 'Never':
        message = "Welcome, I don't think you've visited here before."
    else:
        message = 'Welcome back, last visited: {} secs ago'.format(time.time() -
                last_visit)
    session['last_visit'] = time.time()

    return web.Response(body=message.encode('utf-8'))

async def ws_handler(request):

    session = await get_session(request)

    #print(session.get('last_visit'))

    ws = web.WebSocketResponse()

    await ws.prepare(request)

    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                await ws.close()
            else:
                ws.send_str(msg.data + '/answer')
        elif msg.tp == aiohttp.MsgType.error:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws

async def init(loop):
    app = web.Application()
    #setup(app, SimpleCookieStorage())
    setup(app, EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))
    app.router.add_route('GET', '/', handler)
    app.router.add_route('GET', '/ws', ws_handler)
    srv = await loop.create_server(
        app.make_handler(), '0.0.0.0', 8080)
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
