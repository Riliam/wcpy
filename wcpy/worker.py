from collections import Counter
import string
import json
import zmq
import click


def process_text(text):
    punct_to_space_table = {ord(c): ' ' for c in string.punctuation}
    cleaned_text = text.lower().translate(punct_to_space_table)
    words_list = cleaned_text.split()
    return words_list


@click.command()
@click.option('--broker-host', default='localhost', help='Host of broker')
@click.option('--broker-port', default=12346, help='Port of broker backend socket')
def worker_run(broker_host, broker_port):
    ''' Start worker process, which converts raw text into frequency map.
    '''
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    broker_url = 'tcp://{0}:{1}'.format(broker_host, broker_port)
    socket.connect(broker_url)

    while True:
        message = socket.recv_string()
        print('.')

        words_list = process_text(message)
        counter = Counter(words_list)
        json_str = json.dumps(counter)

        socket.send_string(json_str)


if __name__ == '__main__':
    worker_run()
