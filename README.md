### TODO:
  - Handle when security group is missing (smth is buggy with the creation of security rules)
  - Automatically run ansible playbook (necessary?)
  - Check if server with same name already exists
  - Maybe find a better way to deal with regions

# BW Cloud OTree Server Setup

This project contains scripts to automate the deployment of an OTree app. It creates a BW Cloud instance and prepares ansible playbooks based on the created instances properties. Set up can then be finished by running playbooks contained in the ansible folder. 

The "server_setup" playbook will secure the server and install the otree app. 

If needed, the playbook "ssl_setup" can configure the server to be reachable under a custom domain with SSL.

The playbook "update_project" updates the OTree deployment based on the changes in the linked GitHub Repo (it justs pulls from it basically).

For detailed information on what the script and the playbook do, please read the code. I tried to explain what is done using comments and print statements.

## Instructions 

### 1. Install ansible

* Follow the documentation provided [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-windows)
* Ansible doesn't run on windows. However, you have some options:
  - [official FAQ](https://docs.ansible.com/ansible/latest/user_guide/windows_faq.html#windows-faq-ansible)
  - you could set up a cloud machine or a VM on your computer and use ansible from there

### 2. Clone this repository.
```
git clone git@github.com:LS-Shikano/BwCloud_Server_Setup.git
```

### 3. Create a virtual environment, activate it and install requirements

There are multiple ways to achieve this, one is the following:
```
cd BWCloud_Server_Setup
python -m pip venv env
source env/bin/activate
python -m pip install -r requirements.tx
```

### 4. Create and edit .env file

The script retrieves information by reading environment variables that can be set in a file called ".env".
Copy the example .env file (while in the projects root folder):
``` 
cp example_env_file.env .env
```
Then edit the file with your text editor. It contains explanations of the variables you need to specify. 
### 5. Run script:
```
python main.py
```
### 6. Run ansible playbooks
As described in the instructions displayed by the script, run:
```
cd ansible
ansible-playbook server_setup.yml --vault-password-file=.vault_pw
```
### 7. Optionally set up SSL
**A:** If you want the OTree project to be reachable under a custom domain that is managed by you, add the usual entries to the DNS config. See e.g.: https://docs.hetzner.com/konsoleh/account-management/configuration/dnsadministration/

**B:** If you want the OTree project to be reachable under a custom domain ending with "uni-konstanz.de", 
write an Email to the IT support containing the FQDN (Fully qualified domain name) of the instance this script has just created. Ask them to create an alias for the domain you want the site to run under, e.g.
"cdm-exam.polver.uni.konstanz.de" (this should be the domain you specified in the .env file)
Find the FQDN in the scripts output. As long as the IT support hasn't confirmed
they have set up an alias, you won't be able to set up SSL. That is why there is a seperate playbook for this task. 

Once you have added the needed DNS entries or the IT support has confirmed they have set up an alias, set up SSL by running:
```
ansible-playbook ssl_setup.yml --vault-password-file=.vault_pw
```
## Instructions to update project

Update otree project (pull from repo) with:
```
ansible-playbook update_project.yml --vault-password-file vault_pass.txt
```


