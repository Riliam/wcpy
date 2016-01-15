from collections import Counter
import os
import string
import random

import requests
import click

from .worker import process_text


@click.command()
@click.option('--port', default=8080)
@click.option('--random-strings', is_flag=True)
def spam(port, random_strings):
    url = 'http://localhost:{0}/add-frequencies'.format(port)
    if random_strings:
        for c in range(1000):
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
@click.option('--port', default=8080)
def clear_frequencies(port):
    url = 'http://localhost:{0}/delete-frequencies'.format(port)
    requests.delete(url)
