import sys
sys.path.append('../../')
from urpc import uRPC

class EchoServer(uRPC):
    # Magic ^ starts here: EchoServer (class name) will be autoconverted to function name "echo".
    def worker(self, params):
        if 'question' not in params:
            return {'error': 'no question in parameters! why?'}
        question = params['question']
        return {
            'answer': 'you asked "' + question + '" and the answer is "what?"'
        }

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    u = EchoServer()
    u.main_loop()
