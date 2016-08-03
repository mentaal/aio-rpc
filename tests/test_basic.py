from concurrent.futures._base import TimeoutError
#from asyncio import TimeoutError
import pytest

def test_basic(rpc):
    rpc.loop.run_until_complete(rpc.funcs['block_10ms']())
    assert True

def test_except(rpc):
    with pytest.raises(TimeoutError):
        rpc.loop.run_until_complete(rpc.funcs['block'](2))
