import zmq

def main():
    context = zmq.Context()

    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:12345")

    backend  = context.socket(zmq.DEALER)
    backend.bind("tcp://*:12346")

    zmq.device(zmq.QUEUE, frontend, backend)

    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    main()
