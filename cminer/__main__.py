import click


@click.group()
def cli():
    pass


@cli.command()
def sync():
    from . import sync
    sync.run()


@cli.command()
def run():
    from .core import Game
    game = Game(None)
    game.system.mine_at_level(23)


if __name__ == '__main__':
    cli()
