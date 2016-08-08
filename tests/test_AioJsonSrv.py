import pytest
import json
from aio_rpc.Exceptions import NotFoundError, InvalidParamsError, InternalError
from aio_rpc.JsonRPCABC import JsonRPCABC

@pytest.mark.asyncio
async def test_call(srv):
    result = await srv.obj.add(1,2)
    assert result == 3

    req = srv.request('add', positional_params = [2,2])

    result_json = await srv.process_incoming(req)
    result = json.loads(result_json)
    assert result['result'] == 4

@pytest.mark.asyncio
async def test_call_bad(srv):

    req = srv.request('non_existant_func', positional_params = [2,2], id_num=8)

    result_json = await srv.process_incoming(req)
    e = NotFoundError("'<class 'aio_rpc.Wrapper.Wrapper'>' object has no"
           " attribute 'non_existant_func'")
    expected_result = srv.response_error(e, id_num = 8)


    assert expected_result == result_json

@pytest.mark.asyncio
async def test_call(srv):
    req = srv.request('add', positional_params = [2,2,2], id_num=9)

    result_json = await srv.process_incoming(req)
    e = InvalidParamsError("too many positional arguments")
    expected_result = srv.response_error(e, id_num = 9)

    assert expected_result == result_json

@pytest.mark.asyncio
async def test_call_internal_error(srv):
    req = srv.request('raise_exception', id_num=10)

    result_json = await srv.process_incoming(req)
    result_dict = json.loads(result_json)
    print(result_dict)
    e = InternalError("division by zero")
    expected_result = srv.response_error(e, id_num = 10)

    assert expected_result == result_json

