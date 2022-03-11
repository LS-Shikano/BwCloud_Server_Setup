from jinja2 import Template
import requests
from dotenv import load_dotenv
import os
import base64
import re

load_dotenv()


def get_auth_token():
    data = {
        "auth": {
            "identity": {
                "methods": ["password"], "password": {
                                                        "user": {
                                                            "domain": {
                                                                "name": os.getenv("OS_USER_DOMAIN_NAME")
                                                                },
                                                            "name": os.getenv("OS_USERNAME"),
                                                            "password": os.getenv("OS_PASSWORD")
                                                            }
                }
            },
            "scope": {
                    "project": {
                        "domain": {
                            "name": os.getenv("OS_PROJECT_DOMAIN_NAME")
                        },
                        "name":  os.getenv("OS_PROJECT_NAME")
                    }
                }
            }
        }

    url = "https://idm02.bw-cloud.org:5000/v3/auth/tokens"

    res = requests.post(url, json=data, headers={"Content-Type": "application/json"})

    return res.headers["X-Subject-Token"]


def generate_cloud_config():
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

    stream = os.popen('ssh-add -L')
    ssh_key = stream.read()
    ssh_key = re.search("^(.*?)==", ssh_key).group(0)  # in case command returns more than one key

    data = {
        "user": "user",
        "ssh_key": ssh_key,
        "hostname":  os.getenv("SERVER_HOSTNAME")}

    j2_template = Template(template)

    sample_string_bytes = j2_template.render(data).encode(
        "ascii")  # according to doc, base 64 encoding is required https://docs.openstack.org/api-ref/compute/?expanded=create-server-detail#create-server

    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")

    return base64_string
