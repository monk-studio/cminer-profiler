import click
from ._logger import logger
from .core import Game, Archive


@click.group()
def cli():
    pass


@cli.command()
def update():
    from . import update
    update.run()


@cli.command()
def newgame():
    while True:
        name = click.prompt('Name of your archive')
        if name in Archive.list():
            click.echo('Archive already exist')
        break
    archive = Archive(name)
    game = Game(archive=archive)
    while True:
        cmd = click.prompt('Your next action')
        game.execute(cmd)


@cli.command()
@click.option('--archive', prompt=True, help='Name of your archive')
def resume(archive):
    if archive not in Archive.list():
        logger.info('Archive not exist')
        return
    game = Game(archive=archive)
    while True:
        cmd = click.prompt('Your next action')
        game.execute(cmd)


@cli.command()
def profile():
    pass


if __name__ == '__main__':
    cli()
