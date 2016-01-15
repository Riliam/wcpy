import json
from collections import Counter
import string
import asyncio

import click
from aiohttp import web
import aioredis
import aiozmq
import zmq


async def get_frequencies(socket, text):
    ''' Send text for remote analysing.
    Returns dict of frequencies'''
    socket.write([text.encode('utf-8')])
    resp = await socket.read()
    json_str = resp[0]
    frequencies = json.loads(json_str.decode('utf-8'))
    return frequencies


async def update_frequencies(redis, frequencies):
    ''' Updates storage with new `frequencies`.'''
    for k, v in frequencies.items():
        old_v = await redis.zscore(redis.sorted_set_name, k)
        if old_v is None:
            redis.zadd(redis.sorted_set_name, v, k)
        else:
            redis.zincrby(redis.sorted_set_name, v, k)


async def get_most_frequent_words(redis, count=10):
    ''' Returns top `count` frequent words from storage'''
    r = await redis.zrange(
        redis.sorted_set_name,
        -count,
        -1,
        withscores=True)
    return zip(r[-2::-2], r[::-2])


def render_message(pairs):
    ''' Returns pretty string for given list of key-value paris,
    e.g. [('a', 5), ('b', 10)]'''
    messages_list = ['--- Frequencies report: ---']
    for (k, v) in pairs:
        messages_list.append('{0}: {1}'.format(k.decode(), v))
    messages_list.append('---------------------------')

    rendered = '\n'.join(messages_list)
    return rendered


async def add_frequencies(request):
    ''' Initiates POST `text` analysing; updates Redis with
    new data and prints top 10 words to console.'''
    data = await request.post()
    text = data['text']

    frequencies = await get_frequencies(request.app.zsocket, text)
    await update_frequencies(request.app.redis, frequencies)
    top10_words = await get_most_frequent_words(request.app.redis, 10)

    message = render_message(top10_words)
    print(message)
    return web.Response(body=message.encode())


async def delete_frequencies(request):
    ''' Handler to delete all frequencies data.'''
    await request.app.redis.delete(request.app.redis.sorted_set_name)
    return web.Response(body=b'Deleted')


async def init(
        loop, http_host, http_port, broker_host,
        broker_port, redis_host, redis_port, redis_sorted_set_name):
    ''' Initiates aiohttp, aioredis connection; creates socket stream with broker.'''
    app = web.Application()
    app.router.add_route('POST', '/add-frequencies', add_frequencies)
    app.router.add_route('DELETE', '/delete-frequencies', delete_frequencies)

    handler = app.make_handler()
    srv = await loop.create_server(handler, http_host, http_port)

    app.redis = await aioredis.create_redis((redis_host, redis_port), loop=loop)
    app.redis.sorted_set_name = redis_sorted_set_name

    url = 'tcp://{0}:{1}'.format(broker_host, broker_port)
    app.zsocket = await aiozmq.create_zmq_stream(zmq.REQ, connect=url)
    return app, handler, srv


@click.command()
@click.option('--http-host', default='0.0.0.0', help="Host to run HTTP server")
@click.option('--http-port', default=8080, help="Port to run HTTP server")
@click.option('--broker-host', default='localhost', help="Host of broker")
@click.option('--broker-port', default=12345, help="Port of broker frontend socket")
@click.option('--redis-host', default='127.0.0.1', help='Redis host')
@click.option('--redis-port', default=6379, help='Redis port')
@click.option('--redis-sorted-set-name', default='frequencies',
              help='Redis key to store frequencies map')
def main_run(**kwargs):
    ''' Runs HTTP server. Has access to Redis. Delegates frequencies
    computation to workers and adds result to Redis.

    Waits for inputs in `text` key of POST request to /add-frequencies
    '''

    loop = asyncio.get_event_loop()
    app, handler, srv = loop.run_until_complete(init(loop, **kwargs))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(handler.finish_connections(1.0))
        app.redis.close()
        loop.run_until_complete(app.redis.wait_closed())
        app.zsocket.close()
        loop.run_until_complete(app.finish())
    loop.close()


if __name__ == '__main__':
    main_run()
