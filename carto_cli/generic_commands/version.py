import click

CARTO_CLI_VERSION='0.0.0'

@click.command(help='Prints the version of this application')
@click.pass_context
def version(ctx):
    click.echo(CARTO_CLI_VERSION)
