# uRPC is meatware:
#    just send me a meat if you use this piece of code commercialy
# Feel free to copying and it's always legal until you are good,
# Illegal copying of this code prohibited by real patsan's law!

import aioredis
import json
import logging

from urpc import *

class aiouRPC(uRPC):
    '''Oversimplistic RPC realisation on top of Redis and asyncio.'''
    async def connect(self):
        '''connect to Redis server using options from init.
        You should not use it direct normally, main loop and messages operations call it anyway.'''
        if not self._connect:
            self._connect = await aioredis.create_redis(
                'redis://' + self.config['host'],
                db=int(self.config['db']))
            logging.debug("Connecting to " + self.config['host'] + "/" + str(self.config['db']))
        return self._connect

    async def __call__(self, **params):
        '''syntax corn syrup for client call.
        Normally you will call uRPC as a client like `uRPCClassServer()(parameter="value")`
        or (if you don't have access to class implementation `uRPC("urpcclass")(parameter="value")`'''
        queue = self.construct_queue(uPRCmode.wait)
        resp = await self.message_send(queue, params, wait_for_reply=params.get('wait', True), wait_timeout=self.client_timeout)
        if 'response' in resp: del resp['response']
        return resp

    async def message_send(self, respondent, message, wait_for_reply=False, wait_timeout=10):
        '''send message directly to queue. Normally you should not use it directly'''
        R = await self.connect()
        if wait_for_reply:
            incoming_queue = self.construct_queue(uPRCmode.ask)
            message['response'] = incoming_queue
        await R.rpush(respondent, json.dumps(message, ensure_ascii=False))
        return await self.blpop(incoming_queue, wait_timeout)

    async def blpop(self, queue, timeout):
        '''safe redis.blpop with json passing'''
        message = {}
        R = await self.connect()
        try:
            queue, message = await R.blpop(queue, timeout=timeout)
        except TypeError:
            pass
        if message:
            message = json.loads(message.decode('utf-8'))

        return message

    async def message_wait(self):
        '''wait a message from queue. Normally your should not use it directly'''
        incoming_queue = self.construct_queue(uPRCmode.wait)
        logging.debug("waiting for " + incoming_queue)
        message = await self.blpop(incoming_queue, 180)
        return message

class aiouRPCClientFabric(uRPCClientFabric):
    def __getattr__(self, name):
        if name not in self.clients:
            self.clients[name] = aiouRPC(name, db_conf = self.config)
        return self.clients[name]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        for name, client in self.clients.items():
            logging.debug("closing " + str(name) + " now")
            if client._connect:
                client._connect.close()
