import pytest

@pytest.mark.asyncio
async def test_call(srv):
    result = await srv.obj.add(1,2)
    assert result == 3

    req = srv.request('add', positional_params = [2,2])

    result = await srv.process_incoming(req)
    assert result == 4

