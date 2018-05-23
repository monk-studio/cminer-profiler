import click
from .logger import logger
from cminer.core import Game, Archive, Action


def _game_start(archive_name):
    game = Game(archive=Archive(archive_name))
    while True:
        cmds = game.echo()
        while True:
            cmd_idx = click.prompt('下一步')
            try:
                cmd = cmds.get(int(cmd_idx))
            except ValueError:
                click.echo('指令不正確')
                continue
            if not cmd:
                click.echo('指令不存在')
            else:
                break
        game.execute(cmd)


@click.group()
def cli():
    pass


@cli.command()
def update():
    from . import update
    update.run()


@cli.command(help='新遊戲')
def newgame():
    while True:
        archive = click.prompt('存檔的名字')
        if archive in Archive.list():
            click.echo('存檔已經存在')
            return
        break
    _game_start(archive)


@cli.command(help='繼續遊戲')
@click.option('--archive', prompt=True, help='存檔的名字')
def resume(archive):
    if archive not in Archive.list():
        logger.info('存檔不存在')
        return
    _game_start(archive)


if __name__ == '__main__':
    cli()
