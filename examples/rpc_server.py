from aio_rpc.AioRPCServ import AioRPCServ
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import logging
from credentials import credentials
logger = logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    from tests.test_classes.blocking_class import Blocking

    srv = AioRPCServ(class_to_instantiate=Blocking, timeout=0.8, secure=False,
            credentials=credentials)
    srv.run()

