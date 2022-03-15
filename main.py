from helpers import get_auth_token, generate_cloud_config, get_id, create_sec_group_rule
from helpers import generate_hosts, generate_vault, generate_vault_pw_file, generate_settings
import requests
import time
import re
import os
from dotenv import load_dotenv
import sys
import subprocess
import traceback
from rich.console import Console
from rich.markdown import Markdown


console = Console()

load_dotenv()

console.print("Hello :smiley:")
console.rule("")
with console.status("", spinner="dots"):
    print("-- Retrieving authentication token --")
    token = get_auth_token()

    ##################################################
    print("-- Retrieving image id --")
    image_id = get_id("https://api01.ma.bw-cloud.org:9292/v2/images",
                      "images", os.getenv("OS_IMAGE"), token)

    print("-- Retrievingflavor id --")
    flavor_id = get_id('https://api01.ma.bw-cloud.org:8774/v2.1/flavors',
                       "flavors", os.getenv("OS_FLAVOR"), token)

    ###################################################

    print("-- Searching for the required security_group --")
    Found = get_id('https://api01.ma.bw-cloud.org:9696/v2.0/security-groups', "security_groups",
                   "allow_everything", token)

    if Found is None:
        print("-- Required security group was not found. Creating it now --")
        json2 = {
            "security_group": {
                "name": "allow_everything",
                "description": "This security group will allow all in- and outbund conections.\
                 This is very insecure.\
                 Only use it when you plan to configure a firewall on the server itself.",
            }
        }

        res = requests.post('https://api01.ma.bw-cloud.org:9696/v2.0/security-groups',
                            headers={'content-type': 'application/json',
                                     'X-Auth-Token': token,
                                     },
                            json=json2
                            )

        security_group_id = res.json()["security_group"]["id"]

        create_sec_group_rule("ingress", "udp", security_group_id, token)
        create_sec_group_rule("egress", "udp", security_group_id, token)
        create_sec_group_rule("ingress", "tcp", security_group_id, token)
        create_sec_group_rule("egress", "tcp",  security_group_id, token)

    # Security group already created
    else:
        print("-- Security group already exists --")
    ###################################################
    print("-- Creating instance --")
    json = {
        "server": {
                    "name":  os.getenv("OS_SERVER_NAME"),
                    "imageRef": image_id,
                    "flavorRef": flavor_id,
                    "user_data": generate_cloud_config(),
                    "security_groups": [{"name": "allow_everything"}]
                    }
    }

    res = requests.post('https://api01.ma.bw-cloud.org:8774/v2.1/servers',
                        headers={'content-type': 'application/json',
                                 'X-Auth-Token': token,
                                 },
                        json=json
                        )
    data = res.json()

    try:
        server_id = data["server"]["id"]

    except Exception:
        console.rule("")
        console.print(":warning: Instance creation failed :warning: \n")
        traceback.print_exc()
        print("\n")
        print("-- You can usually find out what went wrong by reading the response to the POST request -- \n")
        print(data)
        console.rule("")
        sys.exit("-- Exiting script --")
        ###################################################

    print("-- Waiting 15 seconds for the instance to be spawned --")
    time.sleep(15)
    print("-- Retrieving instances ip and domain --")
    res = requests.get("https://api01.ma.bw-cloud.org:8774/v2.1/servers/{id}".format(id=server_id),
                       headers={'content-type': 'application/json',
                                'X-Auth-Token': token
                                },
                       )

    data = res.json()["server"]

    ip = data["addresses"]['public-belwue'][0]["addr"]

    # bwCloud Hostname  is not part of the requested json, so it has to be generated manually
    region = data["links"][0]["href"]
    # retrieving region from api link
    region = re.search("(?<=1.)(.*)(?=.bw)", region).group(0)
    bw_cloud_hostname = "{id}.{region}.bw-cloud-instance.org".format(id=server_id, region="ma")

    print("-- Instances IP: {ip} -- ".format(ip=ip))

    console.print("--- :sparkle: Important! The instances FQDN is: \
    \n {domain} :sparkle:-- ".format(domain=bw_cloud_hostname))

    print("-- Preparing ansible playbook execution --")

    print("-- Generating ansible hosts file --")
    generate_hosts(ip)

    print("-- Generating ansible settings file --")
    generate_settings(bw_cloud_hostname)

    print("-- Generating ansible vault pw file --")
    generate_vault_pw_file()

    print("-- Generating ansible vault --")
    generate_vault()

    print("-- Installing ansible requirements --")
    bashCommand = "ansible-galaxy install -r ansible/requirements.yml"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    print("-- Waiting 20 seconds for the instance to start completely --")
    time.sleep(20)

    print("-- Ready for playbook execution --")

# TODO: Automatically run ansible playbook

###############################################

MARKDOWN = """
# What to do now:

1. Write an Email to the IT support containing the FQDN of the instance this script has just
created. Ask them to create an alias for the domain you want the site to run under, e.g.
"cdm-exam.polver.uni.konstanz.de" Find the FQDN above. As long as the IT support hasn't confirmed
they have set up an alias, you won't be able to set up SSL. That is why there is a
seperate playbook for this task.

2. Configure the server with ansible by running the following commands:
```
cd ansible
ansible-playbook server_setup.yml --vault-password-file=.vault_pw
```
3. Once the IT support has confirmed they have set up an alias, set up SSL by running:
```
cd ansible
ansible-playbook ssl_setup.yml --vault-password-file=.vault_pw
```
4. You can optionally update the project in the future by running:
```
ansible-playbook update_project.yml --vault-password-file=.vault_pw
```
"""

md = Markdown(MARKDOWN)
console.rule("")
console.print(md)
console.rule("")
console.print("Bye :smiley:")
