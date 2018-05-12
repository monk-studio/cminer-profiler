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
    from . import run
    run()


if __name__ == '__main__':
    cli()
