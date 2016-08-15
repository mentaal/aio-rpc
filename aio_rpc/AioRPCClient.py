import aiohttp
import asyncio
from .AioJsonClient import AioJsonClient
from .ClientObj import ClientObj
from .Exceptions import NotFoundError

jar = aiohttp.CookieJar(unsafe=True)

class AioRPCClient():
    '''python RPC client, partnered for AioRPCServ'''

    def __init__(self):

        event_loop = asyncio.get_event_loop()
        future_dict = {}
        q = asyncio.Queue(maxsize=5, loop=event_loop)
        json_client = AioJsonClient( event_loop=event_loop, future_dict=future_dict)
        self.client_obj = ClientObj(event_loop=event_loop, q=q, json_client=json_client)

        self.q = q
        self.json_client = json_client
        self.event_loop = event_loop
        asyncio.ensure_future(self.issue_requests(), loop=event_loop)

    async def issue_requests(self):
        async with aiohttp.ClientSession(cookie_jar=jar) as session:
            async with session.get('http://localhost:8080/') as resp:
                #print(resp.status)
                #print(await resp.text())
                print(session.cookies)
                #cookie = session.cookies
                #print(jar._cookies)

            print('cookies: ', session.cookies)
            async with session.ws_connect('http://localhost:8080/ws') as ws:

                while True:
                    request_json = await self.q.get()
                    ws.send_str(request_json)

                    msg = await ws.receive()
                    if msg.tp == aiohttp.MsgType.text:
                        r = await self.json_client.process_incoming(msg.data)
                    elif msg.tp == aiohttp.MsgType.closed:
                        break
                    elif msg.tp == aiohttp.MsgType.error:
                        break

    def run(self, coro):
        #self.event_loop.run_forever()
        loop = self.event_loop
        task = asyncio.ensure_future(coro(self.client_obj), loop=loop)
        loop.run_until_complete(task)
        for task in asyncio.Task.all_tasks(loop=loop):
            task.cancel()
        #loop.run_until_complete()
        loop.stop()

        
        print("closing loop...")
        loop.close()

    #def add_coroutine(self, coroutine):
    #    l = self.event_loop

    #    asyncio.ensure_future(coroutine(self.client_obj, l), loop=l)

