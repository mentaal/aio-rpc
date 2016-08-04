import pytest
import asyncio
from aio_rpc.ObjectWrapper import ObjectWrapper
from test_classes.blocking_class import Blocking

@pytest.fixture(scope='module')
def rpc():
    b = Blocking()
    loop = asyncio.get_event_loop()
    return ObjectWrapper(b,loop, timeout=0.1)

