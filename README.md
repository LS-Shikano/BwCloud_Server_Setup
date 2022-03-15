# documentation_server_setup

This project contains a scripts to automate the deployment of an OTree App. It creates a BW Cloud instance and prepares an ansible project based on the created instances IP etc. Set up can then be finished by running playbooks contained in the ansible folder. The server_setup playbook will secure the server and install the otree app. For detailed information on what the script does, please read the code. I tried to explain what is done using comments and print statements.

## Instructions to create and set up server

1. Install ansible

- Follow the documentation provided [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-windows)
- Ansible doesn't run on windows. However, you have some options:
  - [official FAQ](https://docs.ansible.com/ansible/latest/user_guide/windows_faq.html#windows-faq-ansible)
  - you could set up a cloud machine or a VM on your computer and use ansible from there

2. Clone this repository.

3. Install python requirements

`python -m pip install -r requirements.txt`

4. Create .env file

The script retrieves information by reading environment variables that can be set in a file called ".env".

Example .env file:

```
# OS stands for Open Stack, which is the cloud platform software BW Cloud uses

# Operating system you want the server to run. This project was tested with Ubuntu 20.04
OS_IMAGE="Ubuntu 20.04"

# Type of instance you want the script to create. Visit https://www.bw-cloud.org/de/bwcloud_scope/flavors for available options.
OS_FLAVOR="m1.tiny"

# Name of the server on BW cloud
OS_SERVER_NAME="exam-22"

# Credential needed to get an authentication token. Visit https://portal.bw-cloud.org/project/api_access/ and click "View Credentials"
OS_USERNAME="jonas.stettner@uni-konstanz.de"
OS_PASSWORD="pw"
OS_PROJECT_NAME ="Projekt_jonas.stettner@uni-konstanz.de"


SERVER_HOSTNAME="exam-22"

# User that you will use to log in to the server
SERVER_USER="user"

OTREE_ADMIN_PW="pw"

# Postgre DB password
DB_PW="pw"

ANSIBLE_VAULT_PW="pw"

# This is the domain people will see when using the application
DOMAIN="cdm-exam.polver.uni-konstanz.de"

# Mail address to register the ssl certificate with
CERTBOT_MAIL_ADRESS="hiwis.shikano@uni-konstanz.de"

# This is what the ansible playbook will use the retrieve the otree projects code
GIT_USER="hiwis.shikano"

# Valid access token. Visit https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
GIT_TOKEN="pw"
```

5. Run script:

`python main.py`

6. Follow the instructions displayed during script execution.

## Instructions to update project

Update otree project (pull from repo) with:

`ansible-playbook update_project.yml --vault-password-file vault_pass.txt`

You have to be in the ansible folder for this to work
