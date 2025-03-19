import click


@click.group(short_help="example_extension CLI.")
def example_extension():
    """example_extension CLI.
    """
    pass


@example_extension.command()
@click.argument("name", default="example_extension")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [example_extension]
