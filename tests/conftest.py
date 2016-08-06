import pytest
import asyncio
from aio_rpc.ObjectWrapper import ObjectWrapper
from aio_rpc.Wrapper import Wrapper
from test_classes.blocking_class import Blocking
from aio_rpc.JsonRPCWrapper import JsonRPCABC

@pytest.fixture(scope='module')
def rpc():
    b = Blocking()
    loop = asyncio.get_event_loop()
    return ObjectWrapper(obj=b,loop=loop, timeout=0.1)

@pytest.fixture(scope='module')
def wrapped_obj():
    loop = asyncio.get_event_loop()
    return Wrapper(cls=Blocking,cls_args=None, loop=loop, timeout=0.1)


@pytest.fixture(scope='module')
def json_abc():
    return JsonRPCABC()
