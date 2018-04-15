## Vagrant

### Distribute

For quick distribution see [dist.md](dist.md).  

### Development

    cp vagrant.yml vagrant_local.yml  # Adapt to your needs
    
    vagrant up
    
    # Put your public.key into vagrant
    cat ~/.ssh/id_rsa.pub | vagrant ssh -c 'cat | sudo tee -a ~vagrant/.ssh/authorized_keys'
    cat ~/.ssh/id_rsa.pub | vagrant ssh -c 'cat | sudo tee -a ~rubot/.ssh/authorized_keys'
    
    play up  # Creates env/vagrant

    play book env/vagrant run/provision.yml
    play book env/vagrant run/deploy.yml

#### From within

    vagrant ssh
    sudo -iu rubot
    cd ~/src
    ansible-playbook --vault-password-file vault_pass.txt -i env/local -c local run/provision.yml

    # Optional
    pip install -r requirements.txt

    play book env/local -c local run/deploy.yml
    
    # Reminder
    sudo -Hu www-data -s /bin/bash
    cd /var/www/<project_name>/<project_name>
    drush cr
    
