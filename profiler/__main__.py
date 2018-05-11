import click


@click.group()
def cli():
    pass


@cli.command(help='hello world')
def hello():
    print('hello')


if __name__ == '__main__':
    cli()
