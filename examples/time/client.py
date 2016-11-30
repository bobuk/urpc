import sys, time
from pprint import pprint
sys.path.insert(0, '../../')
from urpc import uRPCClientFabric
rpc = uRPCClientFabric()

if __name__ == '__main__':
    pprint(rpc.time())
    time.sleep(3)
    pprint(rpc.time())

