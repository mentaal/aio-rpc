import json
import pytest
import aio_rpc.Exceptions as Exceptions
from aio_rpc.Exceptions import (
        ParseError,
        InvalidRequestError,
        NotFoundError,
        InvalidParamsError,
        InternalError,
        UnimplementedError)

def test_request_positional(json_abc):

    params = [1,2,3]
    json_obj,id_num = json_abc.request('func_name', positional_params=params)
    request_dict = json.loads(json_obj)
    assert request_dict == { 
            'jsonrpc' : '2.0',
            'method'  : 'func_name',
            'params'  : params,
            'id'      : 0 }


def test_request_parameterised(json_abc):

    params = {
            'arg_1' : 1,
            'arg_2' : 2,
            'arg_3' : 3}
    json_obj,id_num = json_abc.request('func_name', keyword_params=params)
    request_dict = json.loads(json_obj)
    assert request_dict == { 
            'jsonrpc' : '2.0',
            'method'  : 'func_name',
            'params'  : params,
            'id'      : 1 } #id is autoincremented

def test_notification(json_abc):
    params = { 'arg_1' : 1, 'arg_2' : 2, 'arg_3' : 3}
    json_obj,id_num = json_abc.request('func_name', id_num=5, keyword_params=params,
            notification=True)
    request_dict = json.loads(json_obj)
    assert request_dict == { 
            'jsonrpc' : '2.0',
            'method'  : 'func_name',
            'params'  : params}


def test_request_no_params(json_abc):

    json_obj,id_num = json_abc.request('func_name', id_num=0)
    request_dict = json.loads(json_obj)
    assert request_dict == { 
            'jsonrpc' : '2.0',
            'method'  : 'func_name',
            'id'      : 0 }

def test_request_id(json_abc):

    params = {
            'arg_1' : 1,
            'arg_2' : 2,
            'arg_3' : 3}
    json_obj,id_num = json_abc.request('func_name', id_num=5, keyword_params=params)
    request_dict = json.loads(json_obj)
    assert request_dict == { 
            'jsonrpc' : '2.0',
            'method'  : 'func_name',
            'params'  : params,
            'id'      : 5 }

def test_response_result(json_abc):

    json_obj = json_abc.response_result(id_num=5, result=10)
    response_dict = json.loads(json_obj)

    assert response_dict == {
            'jsonrpc' : '2.0',
            'result'  : 10,
            'id'      : 5}



def test_response_error_parse_error(json_abc):

    parse_error_exception = ParseError("invalid json: 'blah!$'")

    json_obj = json_abc.response_error(parse_error_exception)
    response_dict = json.loads(json_obj)

    assert response_dict == {
            'jsonrpc' : '2.0',
            'id'      : 'null',
            'error'  : {
                'code' : -32700,
                'message' : 'Parse Error',
                'data' : {
                    'explanation' : parse_error_exception.__doc__,
                    'details'     : "invalid json: 'blah!$'" } }}


def test_exception_responses(json_abc):
    'test all exception types'
    for c in (
            ParseError,
            InvalidRequestError,
            NotFoundError,
            InvalidParamsError,
            InternalError,
            UnimplementedError):

        exc = c('some message')
        json_obj = json_abc.response_error(exc)
        response_dict = json.loads(json_obj)

        assert response_dict == {
                'jsonrpc' : '2.0',
                'id'      : 'null',
                'error'  : exc.to_json_rpc_dict()}

@pytest.mark.asyncio
async def test_process_incoming_parse_error(json_abc):

    r = await json_abc.process_incoming('{"malformed":"json"')
    response_dict = json.loads(r)
    expected_subset = {
            'jsonrpc' : '2.0',
            'id'      : 'null',
            }
    expected_error = {
                'code' : -32700,
                'message' : 'Parse Error' }

    assert expected_subset.items() <= response_dict.items()
    assert response_dict.get('error') is not None
    assert expected_error.items() <= response_dict['error'].items()

    #print(response_dict)

@pytest.mark.asyncio
async def test_process_incoming_invalid_request(json_abc):

    request,id_num = json_abc.request('1_req', positional_params=[1,2,3], id_num=4)

    r = await json_abc.process_incoming(request)
    expected_e = InvalidRequestError(
            'method cannot be empty or start with a number')

    assert json_abc.response_error(expected_e) == r

@pytest.mark.asyncio
async def test_process_incoming_missing_id(json_abc):

    response = json_abc.response_result(result=5, id_num=4)
    response_obj = json.loads(response)
    response_obj.pop('id')
    response = json.dumps(response_obj)

    r = await json_abc.process_incoming(response)
    expected_e = InvalidRequestError('Missing ID in result')

    result = json_abc.response_error(expected_e)

    assert  result == r

