# -*- coding: utf-8 -*-
import os
import pickle

import click

from play import run, ralign, update_environment
from play.api import cli

update_environment(dict(
    # VAGRANT_SETTINGS='projectB',
))

PICKLE_FILE = '.play.db'
VAGRANT_HOSTNAME = 'default.rubot.vagrant'
VAGRANT_SSH_OPTS = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
VAGRANT_USER = 'vagrant'


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.argument('raw_options', nargs=-1, type=click.UNPROCESSED)
def ssh(ctx, raw_options):
    """SSH to selected environment."""
    command = None

    try:
        cache = pickle.load(open(PICKLE_FILE, "rb"))
        vagrant_ip = cache.get('vagrant_ip')
        command = "ssh -t {} {}@{}".format(
            VAGRANT_SSH_OPTS, VAGRANT_USER, vagrant_ip)
    except IOError:
        click.echo('{} missing. Run `export` task first.'.format(PICKLE_FILE))
        ctx.exit(2)
    except:
        click.echo('Try `export -u` task first.')
        ctx.exit(2)

    run('{}{}'.format(command, ralign(raw_options)))


@cli.command()
@click.option('-u', '--update', is_flag=True, help="Update cache file: {}".format(PICKLE_FILE))
@click.option('-a', '--ansible', is_flag=True, help='Export as ansible inventory file')
def export(update, ansible):
    """Export vagrant environment from running vagrant to cachefile for ssh task and ansible."""
    if update:
        try:
            os.remove(PICKLE_FILE)
        except OSError:
            click.echo("{} not found. Rebuilding.".format(PICKLE_FILE))

    click.echo('If this command hangs just cancle and try again. Check that vagrant is running!')
    if os.path.exists(PICKLE_FILE):
        cache = pickle.load(open(PICKLE_FILE, "rb"))
        vagrant_ip = cache.get('vagrant_ip')
        vagrant_port = cache.get('vagrant_port')
    else:
        vagrant_port, err = run('vagrant port --guest 22', capture=True)
        vagrant_ip, err = run(
            'ssh {} -p {} -q {}@127.0.0.1 cat /myip'.format(
                VAGRANT_SSH_OPTS, vagrant_port, VAGRANT_USER), capture=True)

        pickle.dump(
            dict(vagrant_port=vagrant_port, vagrant_ip=vagrant_ip), open(PICKLE_FILE, "wb")
        )

    if ansible:
        if not os.path.isdir('env'):
            os.mkdir('env')
        with open('env/vagrant', "wb") as f:
            line = "{} ansible_user={} ansible_host={} ansible_ssh_common_args='{}'".format(
                VAGRANT_HOSTNAME, VAGRANT_USER, vagrant_ip, VAGRANT_SSH_OPTS)
            f.write(line)

    click.echo(vagrant_ip + ':' + vagrant_port)
