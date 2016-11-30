import sys
sys.path.append('../../')
from urpc import uRPC
from datetime import datetime

class TimeServer(uRPC):
    def worker(self, params):
        now = datetime.now()
        return {
            x: getattr(now, x) for x in ['hour', 'minute' ,'second']
        }

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    u = TimeServer()
    u.main_loop()
