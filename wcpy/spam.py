import os
import string
import random

import requests
import click

from .worker import process_text


@click.command()
@click.option('--host', default='localhost', help='Host name of HTTP server')
@click.option('--port', default=8080, help='Port of HTTP server')
@click.option('--random-strings', is_flag=True, help='Random strings in input')
def spam(host, port, random_strings):
    ''' Sends some input to /add-frequencies'''
    url = 'http://{0}:{1}/add-frequencies'.format(host, port)
    if random_strings:
        for c in range(10000):
            text = ''.join([random.choice(string.ascii_letters + string.punctuation + '            ') for x in range(1000)])
            requests.post(url, data={'text': text})
    else:
        books = []
        for name in os.listdir('wcpy/texts'):
            with open('wcpy/texts/{0}'.format(name), 'r') as f:
                text = f.read()
                books.append(text)
        for text in books * 3:
            requests.post(url, data={'text': text})


@click.command()
@click.option('--host', default='localhost', help='Host name of HTTP server')
@click.option('--port', default=8080, help='Port of HTTP server')
def clear_frequencies(host, port):
    ''' Deletes all data about frequences for given HTTP connection'''
    url = 'http://{0}:{1}/delete-frequencies'.format(host, port)
    requests.delete(url)
