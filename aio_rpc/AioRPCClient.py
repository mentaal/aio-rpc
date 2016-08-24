import aiohttp
import asyncio
from .AioJsonClient import AioJsonClient
from .ClientObj import ClientObj
from .Exceptions import NotFoundError
import logging


logger = logging.getLogger(__name__)

class AioRPCClient():
    '''python RPC client, partnered for AioRPCServ'''

    def __init__(self):

        event_loop = asyncio.get_event_loop()
        self.jar = aiohttp.CookieJar(unsafe=True, loop=event_loop)
        self.conn = aiohttp.TCPConnector(verify_ssl=False, loop=event_loop)
        future_dict = {}
        q = asyncio.Queue(maxsize=5, loop=event_loop)
        json_client = AioJsonClient( event_loop=event_loop, future_dict=future_dict)
        self.client_obj = ClientObj(event_loop=event_loop, q=q, json_client=json_client)

        self.q = q
        self.json_client = json_client
        self.event_loop = event_loop
        asyncio.ensure_future(self.issue_requests(), loop=event_loop)

    async def shutdown(self):
        '''run all tasks to completion'''
        me = asyncio.Task.current_task()
        for task in asyncio.Task.all_tasks():
            if task == me:
                continue
            task.cancel()
            await asyncio.wait([task])



    async def issue_requests(self):
        async with aiohttp.ClientSession(
                    cookie_jar=self.jar,
                    connector=self.conn,
                    loop=self.event_loop) as session:
            async with session.get('https://localhost:8080/') as resp:
                #logger.debug(resp.status)
                logger.debug(await resp.text())
            for i in range(10):
                async with session.get('https://localhost:8080/get_access') as resp:
                    r = await resp.text()
                    if r == 'Resource granted':
                        logger.debug("resource was granted. continuing")
                        break
                    else:
                        logger.debug("Resource is busy, perhaps try again in a while?")
            else:
                logger.debug("Resource is still busy... giving up!")
                for task in asyncio.Task.all_tasks(loop=self.event_loop):
                    if task == asyncio.Task.current_task(loop=self.event_loop):
                        logger.debug("skipping current task..")
                        continue
                    logger.debug("killing task: {}".format(task))
                    task.cancel()
                #self.event_loop.stop()
                logger.debug("returning..")
                return

            logger.debug("connecting via wss...")
            async with session.ws_connect('wss://localhost:8080/wss', timeout=2) as ws:

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
        loop.run_until_complete(self.shutdown())
        loop.stop()

