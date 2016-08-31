import aiohttp
from aiohttp import BasicAuth
import asyncio
from .AioJsonClient import AioJsonClient
from .ClientObj import ClientObj
from .Exceptions import NotFoundError
import logging


logger = logging.getLogger(__name__)

class AioRPCClient():
    '''python RPC client, partnered for AioRPCServ'''

    def __init__(self, *,
            #host_addr='0.0.0.0',
            host_addr='localhost',
            port=8080,
            timeout=2,
            retry_wait_time = 5,
            retry_attempts = 10,
            login='default',
            pw='123456',
            secure = True
            ):
        '''initialize rpc client.
        Args:
            host_addr (str): the address to connect to
            port (int): the port number to connect to
            timeout (int):the time after which the client gives up connecting to
            the server
            retry_wait_time (int): the time between retrying server for resource if
            it's busy. 
            retry_attempts (int): the amount of times to retry the server
            secure (bool): To connect via https or http
        '''

        event_loop = asyncio.get_event_loop()
        #unsafe=True because could be connecting to server at localhost
        self.jar = aiohttp.CookieJar(unsafe=True, loop=event_loop)
        #using verify_ssl=False because the server could use a self-signed cert
        self.conn = aiohttp.TCPConnector(verify_ssl=False, loop=event_loop)
        future_dict = {}
        q = asyncio.Queue(maxsize=5, loop=event_loop)
        json_client = AioJsonClient( event_loop=event_loop, future_dict=future_dict)
        self.client_obj = ClientObj(event_loop=event_loop, q=q, json_client=json_client)

        self.q = q
        self.json_client = json_client
        self.event_loop = event_loop
        asyncio.ensure_future(self.issue_requests(), loop=event_loop)

        self.host_addr = host_addr
        self.port = port
        self.secure = secure
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_wait_time = retry_wait_time

        logger.debug("Using login: {}, password: {}".format(login,pw))
        self.login_details = BasicAuth(login=login,password=pw)

    async def shutdown(self):
        '''run all tasks to completion'''
        me = asyncio.Task.current_task()
        for task in asyncio.Task.all_tasks():
            if task == me:
                continue
            task.cancel()
            await asyncio.wait([task])

    def make_url(self, path='', use_ws=False):
        if self.secure:
            protocol = 'https'
            ws = 'wss'
        else:
            protocol = 'http'
            ws = 'ws'
        if use_ws:
            protocol = ws
        url =  '{}://{}:{}/{}'.format(protocol, self.host_addr, self.port, path)
        logging.debug("url: {}".format(url))
        return url


    async def issue_requests(self):
        async with aiohttp.ClientSession(
                    cookie_jar=self.jar,
                    connector=self.conn,
                    loop=self.event_loop) as session:
            #async with session.get(self.make_url()) as resp:
            #    #logger.debug(resp.status)
            #    logger.debug(await resp.text())
            async with session.get(
                self.make_url('login'),
                auth=self.login_details) as resp:
                r = await resp.text()
                #print(r)
                if r != 'logged in':
                    print("login error! shutting down..")
                    await self.shutdown()
                    return

            for i in range(self.retry_attempts):
                async with session.get(self.make_url('get_access')) as resp:
                    r = await resp.text()
                    if r == 'Resource granted':
                        logger.debug("resource was granted. continuing")
                        break
                    else:
                        logger.debug("Resource is busy, perhaps try again in a while?")
                        await asyncio.sleep(self.retry_wait_time)
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
            if self.secure:
                proto = 'wss'
            else:
                proto = 'ws'

            logger.debug("connecting via {}...".format(proto))
            async with session.ws_connect(
                    self.make_url(proto, True),
                    timeout=self.timeout) as ws:

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

