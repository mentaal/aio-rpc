import pytest
import json
import asyncio
from aio_rpc.ObjectWrapper import ObjectWrapper
from aio_rpc.Wrapper import Wrapper
from test_classes.blocking_class import Blocking
from aio_rpc.JsonRPCABC import JsonRPCABC
from aio_rpc.AioJsonSrv import AioJsonSrv
from aio_rpc.AioJsonClient import AioJsonClient
from aio_rpc.ClientObj import ClientObj

@pytest.fixture()
def rpc(event_loop):
    b = Blocking()
    return ObjectWrapper(obj=b,loop=event_loop, timeout=0.1)

@pytest.fixture()
def wrapped_obj(event_loop):
    return Wrapper(cls=Blocking,cls_args=None, loop=event_loop, timeout=0.1)


@pytest.fixture(scope='module')
def json_abc():
    return JsonRPCABC()

@pytest.fixture()
def srv(event_loop):
    obj =  Wrapper(cls=Blocking,cls_args=None, loop=event_loop, timeout=0.1)
    return AioJsonSrv(obj=obj)


@pytest.fixture()
def client_mocked(event_loop):
    q = asyncio.Queue(maxsize=5, loop=event_loop)
    c = ClientObj(event_loop=event_loop, q=q)
    future_dict = c._future_dict
    async def answerer(q, future_dict=future_dict):
        request_json = await q.get()
        request_dict = json.loads(request_json)
        id_num = request_dict['id']
        f = future_dict[id_num]
        f.set_result(42)
    asyncio.ensure_future(answerer(q,future_dict),loop=event_loop)


    return c

@pytest.fixture()
def client_srv_answerer(event_loop, srv):
    q = asyncio.Queue(maxsize=5, loop=event_loop)
    c = ClientObj(event_loop=event_loop, q=q)
    future_dict = c._future_dict
    async def answerer(q, future_dict=future_dict, srv=srv):
        request_json = await q.get()
        print("eh?")
        result_json = await srv.process_incoming(request_json)

        result_dict = json.loads(result_json)
        id_num = result_dict['id']
        f = future_dict[id_num]
        f.set_result(result_dict['result'])
    asyncio.ensure_future(answerer(q,future_dict, srv),loop=event_loop)


    return c
