import click
from .logger import logger


def _game_start(archive_name):
    from cminer.core import Archive, Game

    game = Game(archive=Archive(archive_name))
    while True:
        cmds = game.echo()
        while True:
            i = click.prompt('下一步')
            cmd_idx = i.split('|')[0]
            payload = None
            if len(i.split('|')) > 1:
                if i.split('|')[1] != '':
                    payload = int(i.split('|')[1])
            try:
                cmd = cmds.get(int(cmd_idx))
            except ValueError:
                click.echo('指令不正確')
                continue
            if not cmd:
                click.echo('指令不存在')
            else:
                break
        game.execute(cmd, payload)


@click.group()
def cli():
    import sys
    sys.setrecursionlimit(10000)


@cli.command()
def update():
    from . import update
    update.run()


@cli.command(help='新遊戲')
def newgame():
    from cminer.core import Archive

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
    from cminer.core import Archive

    if archive not in Archive.list():
        logger.info('存檔不存在')
        return
    _game_start(archive)


if __name__ == '__main__':
    cli()
