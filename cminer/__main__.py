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


@cli.command(help='自動進行遊戲')
@click.option('--target', prompt=True, help='目標層數', type=int)
def profile(target):
    from uuid import uuid4

    archive_name = uuid4().hex[:6]
    archive = Archive(archive_name)

    game = Game(archive=archive)
    game.click_num = 0

    def _execute(action):
        game.execute(action)
        game.click_num += 1

    while True:
        _execute(Action.shopping)
        _execute(Action.compose)
        _execute(Action.go_mining)
        while game.can_dig():
            _execute(Action.mine)
            if game.archive.mine_progress.level == target:
                _execute(Action.go_camp)
                print(game.archive.warehouse)
                print(f'Clicked {game.click_num} times')
                return
        _execute(Action.go_camp)


if __name__ == '__main__':
    cli()
