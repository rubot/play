
## Play

A fabric-like tool built on [Click](http://click.pocoo.org/6/), that simply runs a [playfile.py](play/templates/playfile-hello/playfile.py).

### Install the play command

    pip install git+ssh://git@github.com/rubot/play.git@master#egg=play

### Setup your project

With play templates: [templates.md](doc/templates.md)  

### Help

    Usage: play [OPTIONS] COMMAND [ARGS]...

      Deployment and Provisioning wrapper.

    Options:
      -C, --compose                   Use docker-compose if provided by subcommand
                                      and a compose-file is in place.
      -v, --verbose                   Verbosity
      -l, --list-commands             List commands
      -ll, --list-templates           List templates
      -f, --playfile TEXT             Which file to run  [default: playfile.py]
      -t, --use-template [vagrant|hello]
                                      Use a playfile-template directly
      --init [playfile-vagrant|vagrant-simple|playfile-hello|vagrant-complex]
                                      Copy template into current directory.
      --version                       Show the version and exit.
      --help                          Show this message and exit.

### Docker compose

The subcommand defined in the playfile must import and use `play.compose`.
Now, if the `-C` switch is given, the commandline is given to `docker-compose run --rm`

Default docker-compose filename: `play-compose.yml`
Can be overriden directly in the playfile with `os.environ['PLAY_COMPOSE_FILE'] = 'path/to/docker-compose.yml'`

### Environment vars

    PLAYFILE
    PLAYTEMPLATE
    PLAY_COMPOSE_FILE
