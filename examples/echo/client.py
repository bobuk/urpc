import sys
from pprint import pprint
sys.path.append('../../')
from urpc import uRPC

if __name__ == '__main__':
    echo = uRPC("echo") # if you prefer, you can import server.py and use EchoServer()
    pprint(echo(blah = "minor"))
    pprint(echo(question = "what is 42?"))
