import pytest
import asyncio
from aio_rpc.AioRPC import AioRPC
from test_classes.blocking_class import Blocking

@pytest.fixture(scope='module')
def rpc():
    b = Blocking()
    loop = asyncio.get_event_loop()
    return AioRPC(b,loop, timeout=0.8)

