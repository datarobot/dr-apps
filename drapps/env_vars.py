from typing import Optional, Dict

import click


def parse_key_value(ctx, param, value):
    res = {}
    try:
        for x in value:
            key, val = x.split('=')
            res[key] = val
        click.echo(f"\n\n\nRes: {res}\n\n\n")
        return res
    except ValueError:
        raise click.BadParameter('Environment variables must be in the format KEY=VALUE')

def parse_key_value(ctx, param, value):
    res = {}
    try:
        for x in value:
            key, val = x.split('=')
            res[key] = val
        return res
    except ValueError:
        raise click.BadParameter('Environment variables must be in the format KEY=VALUE')

@click.command()
@click.option(
    '--stringEnvVar',
    multiple=True,
    type=click.STRING,
    callback=parse_key_value,
    help='String environment variable in the format KEY=VALUE',
)
@click.option(
    '--intEnvVar',
    multiple=True,
    type=click.STRING,
    callback=parse_key_value,
    help='Integer environment variable in the format KEY=VALUE',
)
def env_vars(stringenvvar: Dict[str, str], intenvvar: Dict[str, str]) -> None:
    """Print all environment variable key-value pairs."""
    if not stringenvvar and not intenvvar:
        click.echo("No environment variables provided.")
        return

    click.echo("Environment Variables:")

    for key, value in stringenvvar.items():
        click.echo(f"  {key}: {value} (string)")

    for key, value in intenvvar.items():
        try:
            int_value = int(value)
            click.echo(f"  {key}: {int_value} (integer)")
        except ValueError:
            click.echo(f"  {key}: {value} (invalid integer, treated as string)")