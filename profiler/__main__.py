import click


@click.group()
def cli():
    pass


@cli.command()
def sync():
    from . import sync
    sync.run()


if __name__ == '__main__':
    cli()
