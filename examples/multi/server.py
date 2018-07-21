import sys
sys.path.append('../../')
import logging
logging.basicConfig(level=logging.DEBUG)
from urpc import uRPC
import time

class MultiServer(uRPC):
    def worker(self, params):
        time.sleep(0.3)
        return {
            'number': 'this is process number %s' % (str(self.process_num) if self.process_num >=0 else 'root')
        }

if __name__ == '__main__':
    u = MultiServer()
    u.main_loop_many(9)
