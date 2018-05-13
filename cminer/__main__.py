import click
from ._logger import logger
from .core import Game, Archive


def _game_start(archive_name):
    game = Game(archive=Archive(archive_name))
    game.echo()
    while True:
        cmd = click.prompt('Your next move')
        game.execute(cmd)


@click.group()
def cli():
    pass


@cli.command()
def update():
    from . import update
    update.run()


@cli.command(help='New game')
def newgame():
    while True:
        archive = click.prompt('Name of your archive')
        if archive in Archive.list():
            click.echo('Archive already exist')
            return
        break
    _game_start(archive)


@cli.command(help='Resume game')
@click.option('--archive', prompt=True, help='Name of your archive')
def resume(archive):
    if archive not in Archive.list():
        logger.info('Archive not exist')
        return
    _game_start(archive)


@cli.command(help='Play the game automatically')
def profile():
    pass


if __name__ == '__main__':
    cli()
