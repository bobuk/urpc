# μRPC - simple rpc over Redis in less that 100 lines of code

It's all about hidden magic and syntax corn syrup. For more documentation please read through code.
For your RPC server:

```python
from urpc import uRPC

class AddServer(uRPC):
	def worker(self, params):
		if 'a' not in params or 'b' not in params:
			return {'error': 'you need to provide params "a" and "b"!'}
		return {'summ': params['a'] + params['b']}

server = AddServer()
server.main_loop()
```

Please note what with no arguments AddServer will provide function "add" (lowercase "addserver" without "server").
Also by default it's connected to Redis at localhost and database 1.

On the client side you can use it like this:

```python
from urpc import uRPC

add = uRPC('add')
print(add(a=10, b=20))
```

By default call timeout is 10 seconds. If you need more (or less) call it like

```python

add = uRPC('add').timeout(5)
print(add(a="test", b=" or not"))
```

If you have more than 1 rpc method, you can use `uRPCClientFabric` class to generate it

```python
from urpc import uRPCClientFabric
rpc = uRPCClientFabric({'host': 'localhost', 'db': 3, 'socket_timeout': 10})
print(rpc.add(a=1,b=2))
print(rpc.echo(say='blah'))
```

For convinience urpc also installs `urpc-cli` script for commandline invocation of calls.

```shell
$ urpc-cli add a=10 b=20
{'result': 30}
$ urpc-cli echo say="blahblahblah"
{"echo": "blahblahblah"}
```