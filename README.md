### TODO:
  - Handle when security group is missing (smth is buggy with the creation of security rules)
  - Automatically run ansible playbook (necessary?)
  - Check if server with same name already exists
  - Maybe find a better way to deal with regions

# bwCloud OTree Server Setup

This project contains scripts to automate the deployment of an OTree app. It creates a BW Cloud instance and prepares ansible playbooks based on the created instances properties. Set up can then be finished by running playbooks contained in the ansible folder. 

- The *server_setup* playbook will secure the server and install the OTree app. 

- The playbook *update_project* updates the OTree deployment based on the changes in the linked GitHub Repo (it just pulls from it basically).

For detailed information on what the script and the playbooks do, please read the code. I tried to explain what is done using comments and print statements.

## Instructions 

### 1. Register on bwCloud
Students of the Unversity Konstanz can create one small instance on bwCloud for free.
Follow [these instructions](https://www.bw-cloud.org/de/erste_schritte) to register.

If you want to set up a server inside of the project that the LS Shikano uses on bwCloud, your account needs to be added first. Contact an admin for that.

### 1a.
To access your project on bwCloud, the script needs credentials. One way to do this is using application credentials. If there are no application credentials set up that you have access to, create one by following [this](https://www.bw-cloud.org/de/bwcloud_scope/nutzen#api_token) tutorial.

### 2. Install ansible

* Follow the documentation provided [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-windows)
* Ansible doesn't run on windows. However, you have some options:
  - [official FAQ](https://docs.ansible.com/ansible/latest/user_guide/windows_faq.html#windows-faq-ansible)
  - you could set up a cloud machine or a VM on your computer and use ansible from there

### 3. Clone this repository.
```
git clone git@github.com:LS-Shikano/BwCloud_Server_Setup.git
```

### 4. Create a virtual environment, activate it and install requirements

There are multiple ways to achieve this, one is the following:
```
cd BWCloud_Server_Setup
python -m venv env
source env/bin/activate
python -m pip install -r requirements.tx
```

### 5. Create and edit .env file

The script retrieves information by reading environment variables that can be set in a file called ".env".
Copy the example .env file (while in the projects root folder):
``` 
cp example_env_file.env .env
```
Then edit the file with your text editor. It contains explanations of the variables you need to specify. 
### 6. Run script:
```
python main.py
```
### 7. After having configured your custom domain run the ansible playbook

**A:** If you want the OTree project to be reachable under a custom domain that is managed by you, add the usual entries to the DNS config. See e.g.: https://docs.hetzner.com/konsoleh/account-management/configuration/dnsadministration/

**B:** If you want the OTree project to be reachable under a custom domain ending with "uni-konstanz.de", 
write an Email to the IT support containing the FQDN (Fully qualified domain name) of the instance this script has just created. Ask them to create an alias for the domain you want the site to run under, e.g.
"cdm-exam.polver.uni.konstanz.de" (this should be the domain you specified in the .env file)
Find the FQDN in the scripts output. As long as the IT support hasn't confirmed
they have set up an alias, you won't be able to set up SSL. That is why there is a seperate playbook for this task. 

**C:** If you only want the server to be reachable with the BWCloud hostname, set "DOMAIN=="false" in the .env file.

Once you have added the needed DNS entries or the IT support has confirmed they have set up an alias, set up SSL by running:
```
cd ansible
ansible-playbook server_setup.yml --vault-password-file=.vault_pw
```
## Instructions to update project

Update otree project (pull from repo) with:
```
ansible-playbook update_project.yml --vault-password-file vault_pass.txt
```

## Notes
- Remember to delete servers that you don't need anymore (if it's part of the LS Shikano project it will keep generating costs)
- Create a snapshot before deletion if the server was used for something important (e.g. exam)


