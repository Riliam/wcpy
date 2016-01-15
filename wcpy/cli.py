import click

from .broker import broker_run
from .worker import worker_run
from .main import main_run
from .spam import spam, clear_frequencies


@click.group()
def cli():
    pass


cli.add_command(main_run)
cli.add_command(broker_run)
cli.add_command(worker_run)
cli.add_command(spam)
cli.add_command(clear_frequencies)
