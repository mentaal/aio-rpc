import pytest
# This restores the default Ctrl+C signal handler, which just kills the process
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
from aio_rpc.Exceptions import NotFoundError

@pytest.mark.asyncio
async def test_caller(client_mocked):
    r = await client_mocked.blah_func(1,2,3)
    assert r == 42


@pytest.mark.asyncio
async def test_caller_srv(client_srv_answerer):
    r = await client_srv_answerer.add(1,2)
    assert r == 3

@pytest.mark.asyncio
async def test_caller_srv_bad(client_srv_answerer):
    with pytest.raises(NotFoundError):
        r = await client_srv_answerer.add_bad(1,2)


