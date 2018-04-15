## prep

    echo $VAULT_PASS > vault_pass.txt  # Get VAULT_PASS

### play: using ansible within docker

    alias play='docker-compose run --rm ansible'  # bash
    doskey play='docker-compose run --rm ansible'  # cmd

    cp .env.example .env

### play: using ansible locally

    alias play='ansible-playbook --vault-password-file vault_pass.txt -i'  # bash

#### recommended ansible settings when using ansible locally

    export ANSIBLE_STDOUT_CALLBACK=skippy_extended
    export ANSIBLE_RETRY_FILES_ENABLED=0
    export ANSIBLE_FORCE_COLOR=1
    export ANSIBLE_SSH_PIPELINING=1

## play: run

    play env/dev run/provision.yml
    play env/dev run/deploy.yml

## raw

    docker-compose run --rm ansible
    docker-compose up --build  # Rebuild after changing Dockerfile
    
    docker-compose run --rm ansible env/dev run/provision.yml
    docker-compose run --rm ansible env/dev run/deploy.yml
    docker-compose run --rm --entrypoint="ansible -i" ansible env/dev -m ping all
    docker-compose run --entrypoint bash ansible
    
    ansible-playbook --vault-password-file vault_pass.txt -i env/dev run/provision.yml
    ansible-playbook --vault-password-file vault_pass.txt -i env/dev run/deploy.yml
    ansible -m ping -i env/dev all
    
## update passwords
    
    ansible-vault encrypt passwords.yml
    ansible-vault edit passwords.yml
    ansible-vault rekey passwords.yml  # Change password
    ansible-vault decrypt passwords.yml  # Do not commit unencrypted!

## tags

    play env/vagrant run/do.yml --list-tags
    play env/vagrant run/do.yml -t cu
    play env/vagrant run/do.yml -t cr

    play env/vagrant run/deploy.yml --skip-tags cache-rebuild,composer-update

## vagrant

### development

    cp vagrant.yml vagrant_local.yml
    vagrant up  # follow vagrants output for README
    
    # or add your public.key into your local ~/.ssh/authorized_keys
    cat ~/.ssh/id_rsa.pub | vagrant ssh -c 'cat | sudo tee ~rubot/.ssh/authorized_keys'
    
    PORT=`vagrant port --guest 22` && echo $PORT
    IP=`ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $PORT -q rubot@127.0.0.1 cat /myip` && echo $IP
    
    # follow vagrants output for README
    echo default.rubot.vagrant ansible_host=$IP ansible_ssh_common_args=\'-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null\' > env/vagrant

    play env/vagrant run/provision.yml
    play env/vagrant run/deploy.yml

#### from within

    echo 127.0.0.1 > env/local
    vagrant ssh
    sudo -iu rubot
    cd ~/src
    ansible-playbook --vault-password-file vault_pass.txt -i env/local -c local run/provision.yml
    ansible-playbook --vault-password-file vault_pass.txt -i env/local -c local run/deploy

