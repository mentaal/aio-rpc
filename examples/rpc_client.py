import aiohttp
import asyncio
from aio_rpc.AioRPCClient import AioRPCClient
from aio_rpc.ClientObj import ClientObj
from aio_rpc.Exceptions import NotFoundError

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

async def test_rpc(obj):
    for i in range(100):
        r = await obj.add(i,2)
        print('Result: {}'.format(r))
    print("adding bad task..")
    try:
        r = await obj.add_bad_method(i,2)
    except NotFoundError as e:
        print(e)
        print("NotFoundError exception occurred as method not found")
    print('Result: {}'.format(r))
    print("test_rpc done..")


if __name__ == '__main__':

    client = AioRPCClient()
    #client.add_coroutine(test_rpc)
    client.run(test_rpc)

