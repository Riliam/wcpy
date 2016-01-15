from collections import Counter
import string
import asyncio

from aiohttp import web
import aioredis

REDIS_FREQUENCIES_NAME = 'frequencies'


def process_text(text):
    punct_to_space_table = {ord(c): ' ' for c in string.punctuation}
    cleaned_text = text.lower().translate(punct_to_space_table)
    words_list = cleaned_text.split()
    return words_list


def get_frequencies(text):
    words_list = process_text(text)
    return Counter(words_list)


async def update_frequencies(redis, frequencies):
    for k, v in frequencies.items():
        old_v = await redis.zscore(REDIS_FREQUENCIES_NAME, k)
        if old_v is None:
            redis.zadd(REDIS_FREQUENCIES_KEY, v, k)
        else:
            redis.zincrby(REDIS_FREQUENCIES_KEY, v, k)


async def get_most_frequent_words(redis, count=10):
    r = await redis.zrange(
        REDIS_FREQUENCIES_KEY,
        -count,
        -1,
        withscores=True)
    return zip(r[::2], r[1::2])


def render_message(pairs):
    messages_list = ['--- Frequencies report: ---']
    for (k, v) in pairs:
        messages_list.append('{0}: {1}'.format(k.decode(), v))
    messages_list.append('---------------------------')

    rendered = '\n'.join(messages_list)
    return rendered


async def add_frequencies(request):
    data = await request.post()
    text = data['text']

    frequencies = get_frequencies(text)
    await update_frequencies(request.app.redis, frequencies)
    top10_words = await get_most_frequent_words(request.app.redis, 10)

    message = render_message(top10_words)
    print(message)
    return web.Response(body=message.encode())


async def delete_frequencies(request):
    await request.app.redis.delete(REDIS_FREQUENCIES_KEY)
    return web.Response(body=b'Deleted')


async def init(loop):
    app = web.Application()
    app.router.add_route('POST', '/add-frequencies', add_frequencies)
    app.router.add_route('DELETE', '/delete-frequencies', delete_frequencies)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8080)
    app.redis = await aioredis.create_redis(('127.0.0.1', 6379), loop=loop)
    return app, handler, srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app, handler, srv = loop.run_until_complete(init(loop))
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
        loop.run_until_complete(app.finish())
    loop.close()
