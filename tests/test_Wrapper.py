
def test_function_lookup(wrapped_obj):
    wrapped_obj._loop.run_until_complete(wrapped_obj.block_10ms())

