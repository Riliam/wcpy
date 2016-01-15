import zmq
import click

@click.command()
@click.option('--frontend-port', default=12345)
@click.option('--backend-port', default=12346)
def broker_run(frontend_port, backend_port):
    context = zmq.Context()

    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:{0}".format(frontend_port))

    backend  = context.socket(zmq.DEALER)
    backend.bind("tcp://*:{0}".format(backend_port))

    zmq.device(zmq.QUEUE, frontend, backend)

    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    broker_run()
