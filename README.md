# documentation_server_setup

This project uses ansible to automate the set up of a server hosting an OTree web application.


## General remarks

- This ansible project was tested on an Ubuntu 20.04 instance hosted on bw cloud (with preconfigured default user "ubuntu" and passwordless
sudo enabled)
- important: you need to allow http and https to pass the bw clouds instances firewall

## Instructions

### Install ansible

- Probably just follow the documentation [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-windows)
- Ansible doesn't run on windows. However, you have some options:
  - [official FAQ](https://docs.ansible.com/ansible/latest/user_guide/windows_faq.html#windows-faq-ansible)
  - you could set up a cloud machine or a VM on your computer and use ansible from there

### Clone repo
- Self explanatory

### Install requirements

`ansible-galaxy install -r requirements.yml`

### Set up vault password and ssh keys
- For the current project: find the passwords on the fileserver. I think it would be unsafe to include these files
in the repo.
- For future projects: just encrypt a new secrets.yaml with variables used in the playbooks and add new ssh keys to .ssh/ .
Of course you have to set up the cloud instance with the new ssh key.
- [Documentation on Ansible Vault](https://www.redhat.com/sysadmin/introduction-ansible-vault)

### Run Playbooks:

`ansible-playbook server_setup.yml --vault-password-file vault_pass.txt`

update otree project (pull fromrepo) with:

`ansible-playbook update_project.yml --vault-password-file vault_pass.txt`

Both of these commands will only work if the vault password and the ssh key are in your folder.

## Folder structure:
```
project
│   server_setup.yml ---> Use this playbook to set up the server
│   update_project.yml  ----> Use this playbook to update the otree project
│   hosts.ini ---> The inventory. Change server IP, ssh file path and user here
│   ansible.cfg ---> file in which u have to e.g. specify inventory
│   requirements.yml --> Contains used modules besides core
│   vault_pass.txt ---> Included in .gitignore. Password for ansible vault. Its on the fileserver.
│
└───group_vars
│   │   main.yml ---> Declare unencrypted variables. Most important: Server name and python version.
│   │   secrets.yml ---> Declare encrypted variables, e.g. otree admin password. See instructions above.
│   
└───templates ---> files to copy to server (in .j2 files you can use variables)
│   │   circus.ini ---> config for circus
│   │   envvars.j2 ---> contains linux environment variables to declare
│   │   otree.j2 ---> nginx server config
│
└───.ssh #Included in .gitignore. Contains private and public ssh key. Ask me if u need it.
│   │   exam_server_21_22 ---> private key
│   │   exam_server_21_22.pub ---> public key


```
## Other matters

- To link the server to the uni domain, give IT person the "bwCloud Hostname"

- Testing on fresh install -> rebuild instance instead of creating new one

## Sources

- https://medium.com/@lalit.garghate/handling-openstack-through-apis-1dd9298b68c8
- 
