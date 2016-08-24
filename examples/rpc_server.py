from aio_rpc.AioRPCServ import AioRPCServ
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import logging
#logger = logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    from tests.test_classes.blocking_class import Blocking

    srv = AioRPCServ(Blocking, 0.8)
    srv.run()

