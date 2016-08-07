from asyncio import TimeoutError
import pytest
import time

@pytest.mark.asyncio
async def test_basic(rpc):
    t1 = time.time()
    await rpc._funcs['block_10ms']()
    t2 = time.time()
    print("Delta = {} seconds".format(t2-t1))

@pytest.mark.asyncio
async def test_except(rpc):
    with pytest.raises(TimeoutError):
        await rpc._funcs['block'](2)

@pytest.mark.asyncio
async def test_function_lookup(rpc):
    await rpc.block_10ms()


@pytest.mark.asyncio
async def test_except(rpc):
    with pytest.raises(AttributeError):
        await rpc.undefined_func()
