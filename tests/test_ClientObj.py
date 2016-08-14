import pytest

@pytest.mark.asyncio
async def test_caller(client_mocked):
    r = await client_mocked.blah_func(1,2,3)
    assert r == 42


@pytest.mark.asyncio
async def test_caller_srv(client_srv_answerer):
    r = await client_srv_answerer.add(1,2)
    assert r == 3

