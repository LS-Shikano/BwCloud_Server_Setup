from jinja2 import Template
import requests
from dotenv import load_dotenv
import os
import subprocess
import base64
import re

load_dotenv()


def get_auth_token(os_id, os_secret):
    """
       This function requests an authorization token for BW Clouds Open Stack API. It reads required
        variables from the the bash environment.

       Returns: authorization token of type string

       """
    print(os_id, os_secret)
    data = {
        "auth": {
            "identity": {
                "methods": ["application_credential"], "application_credential": {
                                                            "id": os_id,
                                                            "secret": os_secret
                                                            }
                }
            },
            "scope": {
                    "project": {
                        "domain": {
                            "name": "default"
                        },
                        "id": os.getenv("OS_PROJECT_ID"),
                        "name":  os.getenv("OS_PROJECT_NAME"),
                    }
                }
            }
        

    url = os.getenv("OS_AUTH_URL")

    res = requests.post(url, json=data, headers={
                        "Content-Type": "application/json"})

    return res.headers["X-Subject-Token"]


def generate_cloud_config(user, hostname, ssh_path):
    """
    This function generates a cloud-config file using jinja2. Cloud-config is a tool that allows you
    define e.g. what users and ssh.keys should be set up automatically after the first start of the
    server. Variables are fed into the template by reading the bash environment and by running a
    command that returns the currently used public ssh key. The returned template is then encoded to
    base64, because that is required by the Open Stack API.
    https://cloudinit.readthedocs.io/en/latest/topics/examples.html

    Returns: base64 encoded cloud-config of type string

    """

    template = """
#cloud-config

hostname: {{  hostname  }}
manage_etc_hosts: true
locale: en_US.UTF-8
timezone: Europe/Berlin

users:
- default
- name: {{  user  }}
  groups: sudo
  sudo: "ALL=(ALL) NOPASSWD:ALL"
  lock_passwd: true
  shell: /bin/bash
  ssh_authorized_keys:
    - {{  ssh_key  }}
    """

    ssh_key = txt = open(ssh_path, 'r').read()

    data = {
        "user": user,
        "ssh_key": ssh_key,
        "hostname":  hostname}

    j2_template = Template(template)

    sample_string_bytes = j2_template.render(data).encode(
        "ascii")  # https://docs.openstack.org/api-ref/compute/?expanded=create-server-detail

    base64_bytes=base64.b64encode(sample_string_bytes)
    base64_string=base64_bytes.decode("ascii")

    return base64_string


def get_id(url, type, name, token):
    """
    Requests an id to identify e.g. a flavor or an image.

    Args:
        url (string): valid link to open stack api

        type (string): the type of the object you want to identify ("flavors", "images"...)

        name (string): the name of the object you want to identify (e.g. "Ubuntu 20.04" for images,
        e.g. "m1.tiny" for flavors).

        token (string): valid token for the Open Stack API

    Returns:
        id of type string
    """

    res=requests.get(url,
                       headers = {'content-type': 'application/json',
                                'X-Auth-Token': token
                                },
                       )

    data=res.json()[type]

    result=next((item for item in data if item["name"] == name), None)

    if result is None:
        return
    else:
        return result["id"]


# def create_sec_group_rule(direction, protocol, security_group_id, token):
#     """
#     Creates a security rule inside of a security group.
#
#     Args:
#         direction (string): "ingress" or "egress"
#         protocol (string): "tcp", "udp" or "icmp"
#         security_group_id (string): valid id for a security group you want the rule to be created in
#         token (string): valid token for the Open Stack API
#     """
#
#     json = {
#         "security_group_rule": {
#             "direction": direction,
#             "port_range_min": "1",
#             "ethertype": "IPv4",
#             "port_range_max": "65535",  # highest possible port number
#             "protocol": protocol,
#             "security_group_id": security_group_id,
#             "region": "Freiburg"
#         }
#     }
#
#     requests.post('https://api01.ma.bw-cloud.org:9696//v2.0/security-group-rules',
#                   headers={'content-type': 'application/json',
#                            'X-Auth-Token': token,
#                            },
#                   json=json
#                   )


def generate_hosts(ip):
    """
    Generates a hosts file for ansible using jinja. Writes the rendered string to a file and saves
    it in the ansible folder.

    Args:
        ip (string): the ip you want ansible to execute the playbook for
    """

    template="""
[servers]
server ansible_host={{ ip }}

[all:vars]
ansible_user={{ user }}
    """

    data={
        "ip": ip,
        "user": os.getenv("SERVER_USER")}

    j2_template = Template(template)

    f = open("ansible/hosts", "w")
    f.write(j2_template.render(data))
    f.close()


def generate_settings(bw_cloud_hostname):
    """
    Generates a settings file for ansible using jinja. Writes the rendered string to a file and saves
    it in the ansible folder. Next to the input arguments, this functions reads the environment
    variables DOMAIN and CERTBOT_MAIL_ADRESS which will be used in the playbook.

    Args:
        bw_cloud_hostname (string): the bw_cloud_hostname that ssl should be set up for
    """
    template = """
bw_cloud_hostname: {{ var1 }}
domain: {{ var2 }}
certbot_mail_address: {{ var3 }}
git_repo: {{ var4 }}
    """

    data = {
        "var1": bw_cloud_hostname,
        "var2": os.getenv("DOMAIN"),
        "var3": os.getenv("CERTBOT_MAIL_ADRESS"),
        "var4": os.getenv("GIT_REPO"),
        }

    j2_template = Template(template)

    f = open("ansible/vars/settings.yml", "w")
    f.write(j2_template.render(data))
    f.close()


def generate_vault_pw_file():
    """
    Generates a file containing the password with which the ansible vault can be operated. Reads the
    password from the environment.
    """
    f = open("ansible/.vault_pw", "w")
    f.write(os.getenv("ANSIBLE_VAULT_PW"))
    f.close()


def generate_vault():
    """
    Generates an ansible vault file with variables read from the environment. The file is generated
    with jinja and then encrypted.

    Args:
        ip (string): the ip you want ansible to execute the playbook for
    """
    template = """
otree_admin_pw: {{ pw1 }}
db_password: {{ pw2 }}
git_user: {{  pw3  }}
git_token: {{  pw4  }}
    """

    data = {
        "pw1": os.getenv("OTREE_ADMIN_PW"),
        "pw2": os.getenv("DB_PW"),
        "pw3": os.getenv("GIT_USER"),
        "pw4": os.getenv("GIT_TOKEN")}

    j2_template = Template(template)

    f = open("ansible/vars/vault.yml", "w")
    f.write(j2_template.render(data))
    f.close()

    bashCommand = "ansible-vault encrypt ansible/vars/vault.yml \
    --vault-password-file=ansible/.vault_pw"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
