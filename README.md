# μRPC - simple rpc over Redis in less that 100 lines of code

It's all about hidden magic and syntax corn syrup. For more documentation please read through code.

## Server

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

Please note that with no arguments AddServer will provide function "add" (lowercase "addserver" without "server").
Also by default it's connected to Redis at localhost and database 1.
All defaults can be overridden by environment variable `URPC` or with `.env` file. `URPC` variable must contain string with host and database number, which must be used for rpc. For example, `URPC="localhost:9"`. It works for both, server and client.

Since version 0.3 it's possible to do `server.main_loop_many(N)` where `N` is number of workers which run in parallel.

## Client

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

### Methods fabric

If you have more than 1 rpc method, you can use `uRPCClientFabric` class to generate it

```python
from urpc import uRPCClientFabric
rpc = uRPCClientFabric({'host': 'localhost', 'db': 3, 'socket_timeout': 10})
print(rpc.add(a=1,b=2))
print(rpc.echo(say='blah'))
```

## Async client

If you don't want to wait until rpc request will be processed, you can use asynchronous version of this call

```python
fetch = uRPC('urlfetch')
goo = fetch.wait('http://google.com/')
while not goo.ready():
    time.sleep(1)
print(goo.result)
```

`wait` and `result` also compatible with `uRPCClientFabric` variants.

There's also asyncio-compatible version of uRPC, you can use it by import `aiourpc`:

```python
from aiourpc import aiouRPCClientFabric

async with aiouRPCClientFabric() as rpc:
    pprint(await rpc.fetch('http://ya.ru'))
```


## Command Line tool

For convenience urpc also installs `urpc-cli` script for commandline invocation of calls.

```shell
$ urpc-cli add a=10 b=20
{'result': 30}
$ urpc-cli echo say="blahblahblah"
{"echo": "blahblahblah"}
```
