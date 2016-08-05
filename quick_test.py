import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
import time


def do_something(arg):
    arg -= 1
    #print("Blah blah blah...")



if __name__ == "__main__":
    p_exec = 'process', ProcessPoolExecutor(1)
    t_exec = 'thread', ThreadPoolExecutor(1)
    loop = asyncio.get_event_loop()
    p = partial(do_something, 5)

    for ex_type, ex in (t_exec, p_exec):
        future = loop.run_in_executor(ex, p)

        t1 = time.time()
        loop.run_until_complete(future)
        t2 = time.time()

        print("{} execution took: {} secs".format(ex_type, t2-t1))


