# -*- coding: utf-8 -*-
import os
import re
import shutil
import sys

from os.path import abspath, dirname
from subprocess import call, Popen, PIPE

import click

from click.exceptions import NoSuchOption, BadOptionUsage, UsageError


PACKAGE_DIR = dirname(abspath(__file__))
PLAYFILE = os.environ.get('PLAYFILE', 'playfile.py')
PLAYTEMPLATE = os.environ.get('PLAYTEMPLATE', None)
TEMPLATES_DIR = 'templates'

PLAY_TEMPLATE_PATH = os.path.join(PACKAGE_DIR, TEMPLATES_DIR)
VALID_TEMPLATES = [os.path.join(PLAY_TEMPLATE_PATH, d) for d in os.listdir(PLAY_TEMPLATE_PATH) if os.path.isdir(
    os.path.join(PLAY_TEMPLATE_PATH, d))]

# Merge with user templates
USER_CONF_DIR = os.path.join(os.path.expanduser('~'), '.play')
if not (os.path.exists(USER_CONF_DIR) and os.path.isdir(USER_CONF_DIR)):
    USER_CONF_DIR = None

if USER_CONF_DIR:
    USER_TEMPLATE_PATH = os.path.join(USER_CONF_DIR, TEMPLATES_DIR)
    if os.path.exists(USER_TEMPLATE_PATH) and os.path.isdir(USER_TEMPLATE_PATH):
        for d in os.listdir(USER_TEMPLATE_PATH):
            if os.path.isdir(os.path.join(USER_TEMPLATE_PATH, d)):
                VALID_TEMPLATES.append(os.path.join(USER_TEMPLATE_PATH, d))

VALID_TEMPLATES_DICT = dict([(os.path.basename(d), d,) for d in VALID_TEMPLATES])
VALID_TEMPLATES = VALID_TEMPLATES_DICT.keys()

VALID_TEMPLATES_ALIASES = []
for t in VALID_TEMPLATES:
    if t.startswith('playfile-'):
        VALID_TEMPLATES_ALIASES.extend((t.split('-')[1],))  # t,


class Config(object):

    def __init__(self):
        self.debug = 0
        self.compose = False
        self.playfile = None
        self.use_template = None
        self.user_conf_dir = USER_CONF_DIR
        self.templates = VALID_TEMPLATES_DICT


pass_config = click.make_pass_decorator(Config, ensure=True)


def run(command, capture=False):
    ctx = click.get_current_context()
    if not command:
        ctx.fail('Not a command: {}'.format(command))
    config = ctx.obj
    err = None
    out = None

    _command = noquote_split(command)

    if config.debug:
        click.echo(command)
        if config.debug > 1:
            click.echo(_command)
            click.echo('\n[Dry run]')
            ctx.exit(2)

    try:
        if not capture:
            return call(_command, shell=False)

        err = Popen(_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out = err.communicate()
        try:

            out = out[0].splitlines()[0]
        except:
            click.echo(red('{}\n'.format(out)))
            ctx.fail(command)
    except OSError:
        ctx.fail(command)
    return out, err


def compose(config, command, fspipe=True, compose_file=None, compose_service='ansible'):
    if not isinstance(config, Config):
        abort("compose(config, command, fspipe, compose_file, compose_service). \
            First parameter must be instance of Config class.")
    if config.compose:
        if fspipe:
            _tmpfile = '.play.tmp'
            with open(_tmpfile, "wb") as f:
                f.write('{} $@;rm {}'.format(command, _tmpfile))
            command = 'bash {}'.format(_tmpfile)
        if not compose_file:
            compose_file = os.environ.get('PLAY_COMPOSE_FILE', 'play-compose.yml')
        command = 'docker-compose -f {} run --rm {}{}'.format(compose_file, compose_service, ralign(command))
    return command


def update_environment(environment_dict):
    for e in environment_dict:
        os.environ[e] = environment_dict[e]


def shift(itt, align=False):
    joint = itt if itt else ''
    if getattr(itt, '__iter__', False):
        joint = ' '.join(['"{}"'.format(t) if ' ' in t else t for t in itt]) if itt else ''
    if not joint:
        return ''
    if align == 'right':
        return ' {}'.format(joint)
    if align == 'left':
        return '{} '.format(joint)
    if align == 'center':
        return ' {} '.format(joint)

    return joint


def malign(itt):
    return shift(itt, align='center')


def lalign(itt):
    return shift(itt, align='left')


def ralign(itt):
    return shift(itt, align='right')


def noquote_split(command):
    def _detect_quotes(x):
        return x[1:-1] if x.startswith('"') and x.endswith('"') else x
    return map(_detect_quotes, re.findall(r'(?:"[^"]*"|[^\s"])+', command))


def copytree(src, dst, check_only=False):
    warned = False
    if not os.path.isdir(src):
        abort('Path is not a directory: %s' % src)
    for item in os.listdir(src):
        # if item.startswith('.'):
        #     continue
        if any([item.endswith(pattern) for pattern in ['.DS_Store', '.pyc']]):
            continue
        _s = os.path.join(src, item)
        _d = os.path.join(dst, item)
        if os.path.exists(_d) and check_only:
            warned = True
            warn('Exists: %s' % item)
            continue
        if warned:
            continue
        if not check_only:
            if os.path.isdir(_s):
                shutil.copytree(_s, _d, ignore=shutil.ignore_patterns('.DS_Store', '*.pyc'))
            else:
                shutil.copy2(_s, _d)
        else:
            yell(item)
    return not warned


def yell(msg=''):
    click.echo(yellow(msg, True))


def warn(msg=''):
    click.echo(magenta(msg))


def abort(msg='', status=1):
    click.echo(red('{}\n'.format(msg)))
    sys.exit(status)


def info(msg=''):
    click.echo(green(msg, True))


def green(msg, bold=False):
    return click.style(msg, fg='green', bold=bold)


def red(msg, bold=False):
    return click.style(msg, fg='red', bold=bold)


def yellow(msg, bold=False):
    return click.style(msg, fg='yellow', bold=bold)


def magenta(msg, bold=False):
    return click.style(msg, fg='magenta', bold=bold)


class MyCLI(click.MultiCommand):

    playfile = None
    use_template = None
    cli = None
    commands = []

    def __init__(self, *args, **kwargs):
        self.playfile = kwargs.pop('playfile')
        self.use_template = kwargs.pop('use_template')
        # self.allow_interspersed_args = False
        # self.allow_extra_args = False
        kwargs.update(invoke_without_command=True)
        click.MultiCommand.__init__(self, *args, **kwargs)

        foo = click.get_os_args() or ['-f', self.playfile]
        ctx = self.make_context(__name__, foo, resilient_parsing=True)

        # for _on in self.get_help_option_names(ctx):
        #     if _on in click.get_os_args():
        #         ctx.exit(click.echo('{}\n'.format(ctx.get_help())))

        playfile = ctx.params.get('playfile', False)
        use_template = ctx.params.get('use_template', False) or PLAYTEMPLATE
        if playfile:
            self.playfile = playfile
        if use_template:
            if not use_template.startswith('playfile-'):
                use_template = 'playfile-{}'.format(use_template)
            self.playfile = os.path.join(VALID_TEMPLATES_DICT.get(use_template), playfile)

        try:
            ns = {}
            fn = os.path.join(self.playfile)
            # import sys
            # sys.argv.remove('-f')
            # sys.argv.remove('zplayfile.py')
            # click.echo(click.get_os_args())
            ctx = self.make_context(__name__, click.get_os_args())
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)

            self.cli = ns['cli']
            self.commands = self.cli.list_commands(self.cli)
        except KeyError:
            abort('Not a valid playfile: %s' % self.playfile)
        except (NoSuchOption, BadOptionUsage, UsageError):
            click.echo('{}\n'.format(ctx.get_help()))
        except IOError:
            if ctx.params.get('init', None):
                return
            if ctx.params.get('list_templates', False):
                return
            if os.environ.get('PLAYFILE'):
                warn('env PLAYFILE: {}'.format(os.environ.get('PLAYFILE')))
            if os.environ.get('PLAYTEMPLATE'):
                warn('env PLAYTEMPLATE: {}'.format(os.environ.get('PLAYTEMPLATE')))
            ctx.exit("\nFatal error: Couldn't find any playfiles!\n\n" +
                     "Remember that -f can be used to specify playfile path, and use --help for help")

    def list_commands(self, ctx):
        return self.commands

    def get_command(self, ctx, name):
        if name not in self.commands:
            return
        return self.cli.get_command(self.cli, name)


@click.command(
    cls=MyCLI,
    playfile=PLAYFILE,
    use_template=None,
    no_args_is_help=False
)
@pass_config
@click.pass_context
@click.option('-C', '--compose', is_flag=True,
              help="Use docker-compose if provided by subcommand and a compose-file is in place.")
@click.option('-v', '--verbose', count=True, help="Verbosity")
@click.option('-l', '--list-commands', is_flag=True, help="List commands")
@click.option('-ll', '--list-templates', is_flag=True, help="List templates")
@click.option('-f', '--playfile', help="Which file to run", default=PLAYFILE, show_default=True)
@click.option('-t', '--use-template', help="Use a playfile-template directly", type=click.Choice(
    VALID_TEMPLATES_ALIASES))
@click.option(
    '--init', type=click.Choice(VALID_TEMPLATES),
    help="Copy template into current directory.")
@click.version_option()
def cli(ctx, config, compose, verbose, list_commands, list_templates, playfile, use_template, init):
    """Deployment and Provisioning wrapper."""
    if verbose > 0:
        config.debug = verbose

    if list_templates:
        if config.debug > 0:
            ctx.exit('\n'.join([VALID_TEMPLATES_DICT[k] for k in sorted(VALID_TEMPLATES_DICT)]))
        ctx.exit('\n'.join(sorted(VALID_TEMPLATES)))

    if init:
        try:
            if not copytree(VALID_TEMPLATES_DICT.get(init), os.getcwd(), check_only=True):
                info('Did nothing as some paths already existed.')
            else:
                copytree(VALID_TEMPLATES_DICT.get(init), os.getcwd())
                info('Play files created using {} template.'.format(init))
        except OSError as err:
            abort(err.message)
        except:
            raise
        ctx.exit()

    if list_commands:
        click.echo('\n'.join(ctx.command.list_commands(ctx)))
        ctx.exit()

    if not ctx.invoked_subcommand:
        click.echo(ctx.command.get_help(ctx))
        ctx.exit()

    config.compose = compose
    config.playfile = playfile
    config.use_template = use_template
