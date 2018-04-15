## Intentional way of play

Deployment/Provisioning is provided via [`ansible`](http://docs.ansible.com/ansible/intro_installation.html).  
You can either use ansible locally, or run it within a docker container.  
Please read: [ansible.md](https://code.rubot.de/tools/play/doc/ansible.md).  

For distribution to the customer there is a Vagrantfile prepared under _dist/_  
For local development there is in the main folder a Vagrantfile which should not be edited directly.  
Next to it a `vagrant.yml` for configuration. Please copy it to `vagrant_local.yml` for local adaptions.  
Look at [vagrant.md](https://code.rubot.de/tools/play/doc/vagrant.md) for details.  

For easier dealing with ansible there is the [`play`](https://code.rubot.de/tools/play) command script.  
Please see more documentation there: [`play`](https://code.rubot.de/tools/play/README.md)

Play is just used as shortcut for ansible commands like `ansible-playbook`.  
You can see the power by adding raw_options behind play commands: 
  
    play book env/vagrant run/provision.yml -h

If you don´t want to use `play`, or for background informations see [`raw`](https://code.rubot.de/tools/play/doc/raw.md).  


CONVENTIONS:

* Place ansible _inventory_ files into _env/_
* Place ansible _playbooks_ into _run/_
* Create a `vault_pass.txt` file which contains the ansible vault password for files in _run/encrypted_
* Place code only into the _src_ folder. The first level is reserved for deploying and project configuration

### Master password

The vault password is used for decryption of [ansible-vault](http://docs.ansible.com/ansible/playbooks_vault.html) encrypted files.  
Place deployment relevant passwords into files under _run/encrypted/`name`.yml_.

    echo $VAULT_PASS > vault_pass.txt  # Get VAULT_PASS

### play: run

    play book env/dev run/provision.yml
    play book env/dev run/deploy.yml

#### play: using ansible within docker

When you are on Windows or just don´t want to use a local installed ansible.

    cp .env.example .env  # Adapt to your path

    play book -D env/dev run/provision.yml

### play: help

    Usage: play [OPTIONS] COMMAND [ARGS]...

      Deployment and Provisioning wrapper.

    Options:
      -D, --docker              Use docker if provided by subcommand
      -v, --verbose             Verbosity
      -l, --list-commands       List commands
      -f, --playfile TEXT       Which file to run
      --init [base|full|light]  Copy playfile template into current directory and
                                quit.
      --help                    Show this message and exit.

    Commands:
      book   Run ansible playbook on selected environment.
      ssh    SSH to selected environment.
      up     Export vagrant environment from running...
      vault  Shortcut for ansible-vault.

### play: tags

Example of usage:

    play book env/vagrant run/do.yml --list-tags
    play book env/vagrant run/do.yml -t <tag>

    play book env/vagrant run/deploy.yml --skip-tags <tag>

### play: extra-vars

Example of usage:

    play book env/vagrant run/deploy.yml -e "core_sync=yes"

### play: update deployment passwords
    
    # Optional
    export EDITOR='subl -w'

    play vault run/encrypted/passwords.yml view
    play vault run/encrypted/passwords.yml edit
