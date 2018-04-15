## Vagrant machine for distribution

### Distribute

Send the [Vagrantfile](Vagrantfile) and instructions to the customer.

Place the file in an empty folder.

    vagrant up

Local requirements:

* [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)

### Update (Files and Database)

> Drupal way

Create a new `nucleus-dump.tar` file and provide it to the customer for updates.

    ansible-playbook --vault-password-file vault_pass.txt -i env/dev run/do.yml -t archive-dump
    cd dist
    vagrant up --provision

