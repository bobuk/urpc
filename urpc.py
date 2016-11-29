import redis
from enum import Enum
import string, random
import json
import logging

class uPRCmode(Enum):
    none = 0
    ask = 1
    wait = 2
    finish = 10

config = dict(
    host = "localhost",
    db = 5,
    socket_timeout = 60)

class uRPC:
    def __init__(self, name = None, db_conf=config):
        if not name:
            name = self.__class__.__name__.lower()
            if name.endswith('server'):
                name = name[:-6]
        self.name = name
        self.config = db_conf
        self._connect = None
        self.client_timeout = 10
        
    def connect(self):
        if not self._connect:
            self._connect = redis.Redis(
                host=self.config['host'],
                db=self.config['db'],
                socket_timeout=self.config['socket_timeout'])
            logging.debug("Connecting to " + self.config['host'] + "/" + str(self.config['db']))
        return self._connect

    def construct_queue(self, mode):
        if mode == uPRCmode.wait:
            return 'queue:' + self.name
        elif mode == uPRCmode.ask:
            return 'response:' + self.name + ':' + ''.join(
                random.choice(string.ascii_uppercase) for x in range(12))
        return None

    def main_loop(self):
        while True:
            message = self.message_wait()
            if message:
                logging.info("message is " + json.dumps(message, ensure_ascii=False))
                result = {}
                result = self.worker(message)
                if 'response' in message:
                    _r = message['response']
                    logging.debug("sending back to " + _r + \
                                  "-> " + json.dumps(result, ensure_ascii=False))
                    del message['response']
                    self.message_send(_r, result, wait_for_reply = False)
            logging.debug("tick")
    
    def worker(self, params):
        logging.debug("got hit with " + json.dumps(params, ensure_ascii=False))
        return {}

    def timeout(self, sec):
        self.client_timeout = sec
        return self

    def __call__(self, **params):
        queue = self.construct_queue(uPRCmode.wait)
        resp = self.message_send(queue, params, wait_for_reply=True, wait_timeout=self.client_timeout)
        if 'response' in resp: del resp['response']
        return resp

    def message_send(self, respondent, message, wait_for_reply=False, wait_timeout=10):
        R = self.connect()
        if wait_for_reply:
            incoming_queue = self.construct_queue(uPRCmode.ask)
            message['response'] = incoming_queue
        R.rpush(respondent, json.dumps(message, ensure_ascii=False))
        result = {}
        if wait_for_reply:
            result = self.blpop(incoming_queue, wait_timeout)
        return result

    def blpop(self, queue, timeout):
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
        incoming_queue = self.construct_queue(uPRCmode.wait)
        logging.debug("waiting for " + incoming_queue)
        message = self.blpop(incoming_queue, 180)
        return message

class EchoServer(uRPC):
    def worker(self, params):
        return {'you said': params}

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    u = EchoServer()
    u.main_loop()
    
    # (call it now as uRPC('echo')(alpha = 'omega')
