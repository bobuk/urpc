import sys, time, asyncio
from pprint import pprint
sys.path.insert(0, '../../')
from aiourpc import aiouRPCClientFabric

async def main(loop):
    async with aiouRPCClientFabric() as rpc:
        pprint(await rpc.time())
        await asyncio.sleep(1.0)
        await main2(loop)
        pprint(await rpc.time())

async def main2(loop):
    # also you can manualy call fabric() and .close() after that
    rpc = aiouRPCClientFabric()
    pprint(await rpc.time())
    await asyncio.sleep(1.0)
    pprint(await rpc.time())
    await rpc.close()
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
