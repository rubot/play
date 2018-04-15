import click

from play import pass_config, compose
from play.api import cli


##
# Uncomment to change the default path to play docker-compose.yml
##
# import os
# os.environ['PLAY_COMPOSE_FILE'] = 'path/to/docker-compose.yml'

###
# http://click.pocoo.org/6/
###


@cli.command()
@pass_config
def hello(config):
    click.echo(compose(config, 'world (http://click.pocoo.org/6/)'))
