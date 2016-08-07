import pytest
import asyncio
from aio_rpc.ObjectWrapper import ObjectWrapper
from aio_rpc.Wrapper import Wrapper
from test_classes.blocking_class import Blocking
from aio_rpc.JsonRPCABC import JsonRPCABC
from aio_rpc.AioJsonSrv import AioJsonSrv

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
