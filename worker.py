from collections import Counter
import string
import json
import zmq


def process_text(text):
    punct_to_space_table = {ord(c): ' ' for c in string.punctuation}
    cleaned_text = text.lower().translate(punct_to_space_table)
    words_list = cleaned_text.split()
    return words_list


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect('tcp://localhost:12346')

    while True:
        message = socket.recv_string()
        print(message)

        words_list = process_text(message)
        counter = Counter(words_list)
        json_str = json.dumps(counter)

        socket.send_string(json_str)


if __name__ == '__main__':
    main()
