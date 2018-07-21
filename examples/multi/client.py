import sys
from pprint import pprint
sys.path.append('../../')
import logging
logging.basicConfig(level=logging.INFO)

from urpc import uRPCClientFabric
rpc = uRPCClientFabric()

from uparallel import uparallel

@uparallel(5)
def get_res():
    return rpc.multi()

if __name__ == '__main__':
    res = [get_res() for x in range(1000)]
    for line in res:
        pprint(line())
