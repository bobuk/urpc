# uRPC is meatware:
#    just send me a meat if you use this piece of code commercialy
# Feel free to copying and it's always legal until you are good,
# Illegal copying of this code prohibited by real patsan's law!

import redis
from enum import Enum
import string, random
import json
import logging

# I think what what this code is more or less self-explaining
# but i'll add some docstrings, because its legit.

# logging.basicConfig(level=logging.DEBUG)

config = dict(
    host = "localhost",
    db = 1,
    socket_timeout = 60)

try:
    from defaultenv import ENVC as env
    if ':' in env.urpc:
        host, db = env.urpc.split(':')
        config[host] = host
        config[db] = db
except:
    logging.debug('Default configuration used')

class uPRCmode(Enum):
    '''List of possible positions for internal state code'''
    none = 0
    ask = 1
    wait = 2
    finish = 10

class uRPCAsyncAnswer:
    def __init__(self, queue, db):
        self.db = db
        self.queue = queue
        self.__result = {}

    @property
    def result(self):
        if not self.__result:
            self.ready()
        return self.__result

    def ready(self):
        res = self.db.lpop(self.queue)
        if res:
            self.__result = json.loads(res.decode('utf-8'))
            return True
        return False

class uRPC:
    '''Oversimplistic RPC realisation on top of Redis.'''
    def __init__(self, name = None, db_conf=config):
        '''create new RPC object (for both, client or server)
        Params:
        :name: (optional) name of function which is will be used to name pipe in redis.
              If None then name of the class without "server" at the end will be used.
        :db_config: (optional) dict contains keys
              "host" (host of redis, "localhost" is default),
              "db" (number of redis's db, 1 is default),
              "socket_timeout" (default redis server timeout, 60 sec is default)
        '''
        if not name:
            name = self.__class__.__name__.lower()
            if name.endswith('server'):
                name = name[:-6]
        self.name = name
        self.config = db_conf
        self._connect = None
        self.client_timeout = 10
        self.setup()

    def setup(self):
        '''placeholder for your mixins.
        Always invoked after object creation.'''
        pass

    def connect(self):
        '''connect to Redis server using options from init.
        You should not use it direct normally, main loop and messages operations call it anyway.'''
        if not self._connect:
            self._connect = redis.Redis(
                host=self.config['host'],
                db=self.config['db'],
                socket_timeout=self.config['socket_timeout'])
            logging.debug("Connecting to " + self.config['host'] + "/" + str(self.config['db']))
        return self._connect

    def construct_queue(self, mode):
        '''construct the name of queue or response for replay'''
        if mode == uPRCmode.wait:
            return 'queue:' + self.name
        elif mode == uPRCmode.ask:
            return 'response:' + self.name + ':' + ''.join(
                random.choice(string.ascii_uppercase) for x in range(12))
        return None

    def main_loop(self):
        '''mail loop for RPC server implementation.
        Wait until message will happened and call self.worker(params).
        After that returned dictionary will be sent back to invoker as a result'''
        while True:
            message = self.message_wait()
            if message:
                logging.info("message is " + json.dumps(message, ensure_ascii=False))
                result = {}
                result = self.worker(message)
                if not result:
                    result = {}
                elif type(result) != dict:
                    result = {'result': result}
                if 'response' in message:
                    _r = message['response']
                    logging.debug("sending back to " + _r + \
                                  "-> " + json.dumps(result, ensure_ascii=False))
                    del message['response']
                    self.message_send(_r, result, wait_for_reply = False)
            logging.debug("tick")
    
    def worker(self, params):
        '''this method should be overlapped by your implementation.
        All server works must be implemented here.
        Params:
            :params: dict of parameters from client
        Return: dict (it's mandatory!) of returned values'''
        logging.debug("got hit with " + json.dumps(params, ensure_ascii=False))
        return {}

    def timeout(self, sec):
        '''set timeout for client call. Use it chained like `uRPC("echo").timeout(10)(test="call")`
        Params:
            :sec: number of timeout seconds
        Return:
            self, for chained use'''
        self.client_timeout = sec
        return self

    def __call__(self, **params):
        '''syntax corn syrup for client call.
        Normally you will call uRPC as a client like `uRPCClassServer()(parameter="value")`
        or (if you don't have access to class implementation `uRPC("urpcclass")(parameter="value")`'''
        queue = self.construct_queue(uPRCmode.wait)
        resp = self.message_send(queue, params, wait_for_reply=True, wait_timeout=self.client_timeout)
        if 'response' in resp: del resp['response']
        return resp

    def wait(self, **params):
        '''syntax mayo for async calls.
        Just use `w = urpc("urpcclass").wait()` to get uRPCAsyncAnswer instead of direct answer.
        After that you can check `w.ready()` until it returns `True` or just check out `w.result`
        for a result'''
        queue = self.construct_queue(uPRCmode.wait)
        response_queue = self.message_send(queue, params, wait_for_reply=True, wait_timeout = -1)
        return uRPCAsyncAnswer(response_queue, self.connect())

    def message_send(self, respondent, message, wait_for_reply=False, wait_timeout=10):
        '''send message directly to queue. Normally you should not use it directly'''
        R = self.connect()
        if wait_for_reply:
            incoming_queue = self.construct_queue(uPRCmode.ask)
            message['response'] = incoming_queue
        R.rpush(respondent, json.dumps(message, ensure_ascii=False))
        result = {}
        if wait_for_reply:
            if wait_timeout == -1:
                return incoming_queue
            result = self.blpop(incoming_queue, wait_timeout)
        return result

    def blpop(self, queue, timeout):
        '''safe redis.blpop with json passing'''
        message = {}
        R = self.connect()
        try:
            queue, message = R.blpop(queue, timeout=timeout)
        except redis.exceptions.TimeoutError:
            pass
        except TypeError:
            pass
        if message:
            message = json.loads(message.decode('utf-8'))

        return message

    def message_wait(self):
        '''wait a message from queue. Normally your should not use it directly'''
        incoming_queue = self.construct_queue(uPRCmode.wait)
        logging.debug("waiting for " + incoming_queue)
        message = self.blpop(incoming_queue, 180)
        return message

class uRPCClientFabric:
    def __init__(self, db_config=config):
        '''fabric for uRPC clients.
        Params:
            :db_config: config for redis connection (see uRPC)'''
        self.clients = {}
        self.config = db_config

    def __getattr__(self, name):
        if name not in self.clients:
            self.clients[name] = uRPC(name, db_conf = self.config)
        return self.clients[name]

        
