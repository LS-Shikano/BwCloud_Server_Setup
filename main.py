from helpers import get_auth_token, generate_cloud_config, get_id
# from helpers import create_sec_group_rule
from helpers import generate_hosts, generate_vault, generate_vault_pw_file, generate_settings
import requests
import time
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
    if os.getenv("OS_REGION_NAME") == "Freiburg":
        region = "fr"
    else:
        console.rule("")
        console.print(":warning: Script execution failed :warning: \n")
        print("\n")
        print("-- Our project only allows creating instances in the region 'Freiburg' -- \n")
        console.rule("")
        sys.exit("-- Exiting script --")

    print("-- Retrieving authentication token --")
    token = get_auth_token(os.getenv("OS_ID"), os.getenv("OS_SECRET"))

    ##################################################
    print("-- Retrieving image id --")
    image_id = get_id("{x}/v2/images".format(x=os.getenv("OS_IMAGE_SERVICE_URL")),
                      "images", os.getenv("OS_IMAGE"), token)

    print("-- Retrieving flavor id --")
    flavor_id = get_id("{x}/flavors".format(x=os.getenv("OS_COMPUTE_SERVICE_URL")),
                       "flavors", os.getenv("OS_FLAVOR"), token)

    ###################################################

    print("-- Searching for the required security_group --")

    Found = get_id("{x}//v2.0/security-groups".format(x=os.getenv("OS_NETWORK_SERVICE_URL")),
                   "security_groups", "allow_everything", token)

    if Found is None:
        print("-- Required security group was not found. Creating it now --")
        # json2 = {
        #     "security_group": {
        #         "name": "allow_everything",
        #         "description": "This security group will allow all in- and outbund conections.\
        #      This is very insecure.\
        #      Only use it when you plan to configure a firewall on the server itself.",
        #     }
        #     }
        #
        # res = requests.post("{x}//v2.0/security-groups".format(x=os.getenv("OS_NETWORK_SERVICE_URL")),
        #                     headers={'content-type': 'application/json',
        #                              'X-Auth-Token': token,
        #                              },
        #                     json=json2
        #                     )
        #
        # security_group_id = res.json()["security_group"]["id"]
        #
        # create_sec_group_rule("ingress", "udp", security_group_id, token)
        # create_sec_group_rule("egress", "udp", security_group_id, token)
        # create_sec_group_rule("ingress", "tcp", security_group_id, token)
        # create_sec_group_rule("egress", "tcp",  security_group_id, token)

        # Security group already created
    else:
        print("-- Security group already exists --")
    ###################################################

    print("-- Creating instance --")
    json = {
                      "server": {
                          "name":  os.getenv("SERVER_NAME"),
                          "imageRef": image_id,
                          "flavorRef": flavor_id,
                          "user_data": generate_cloud_config(os.getenv("SERVER_USER"), os.getenv("SERVER_NAME"), os.getenv("SSH_PATH")),
                          "security_groups": [{"name": "allow_everything"}]
                          }
                      }

    res = requests.post("{x}/servers".format(x=os.getenv("OS_COMPUTE_SERVICE_URL")),
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
        print(
                      "-- You can usually find out what went wrong by reading the response to the POST request -- \n")
        print(data)
        console.rule("")
        sys.exit("-- Exiting script --")
        ###################################################

    print("-- Waiting 15 seconds for the instance to be spawned --")
    time.sleep(15)
    print("-- Retrieving instances ip and domain --")

    res = requests.get("{x}/servers/{id}".format(x=os.getenv("OS_COMPUTE_SERVICE_URL"), id=server_id),
                       headers={'content-type': 'application/json',
                                'X-Auth-Token': token
                                },
                       )

    data = res.json()["server"]

    ip = data["addresses"]['public'][0]["addr"]

    # bwCloud Hostname  is not part of the requested json, so it has to be generated manually
    bw_cloud_hostname = "{id}.{region}.bw-cloud-instance.org".format(
            id=server_id, region=region)

    print("-- Instances IP: {ip} -- ".format(ip=ip))

    console.print("[green]-- :sparkle: Important! The instances FQDN is: :sparkle: --")
    console.print("[blue underline]{link}".format(link=bw_cloud_hostname))

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
    bashCommand = "ansible-galaxy install -r ansible/requirements.yml --force"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    print("-- Waiting 20 seconds for the instance to start completely --")
    time.sleep(20)

    print("-- Ready for playbook execution (though sometimes you even need to wait longer for server startup)--")

    ###############################################

    MARKDOWN = """
# What to do now:

The server was created and you need to configure it with an Ansible Playbook. The Playbook includes setting up SSL (https), so there are three options:

A: If the custom domain is managed by you, just add the usual entries
to the DNS config. (https://docs.hetzner.com/konsoleh/account-management/configuration/dnsadministration/)

B: If you want the OTree project to be reachable under a custom domain ending with "uni-konstanz.de", 
write an Email to the IT support containing the FQDN of the instance this script has just
created. Ask them to create an alias for the domain you want the site to run under, e.g.
"cdm-exam.polver.uni.konstanz.de" (this should be the domain you specified in the .env file)
Find the FQDN above. As long as the IT support hasn't confirmed
they have set up an alias, you won't be able to set up SSL. That is why there is a
seperate playbook for this task. 

C: If you have set DOMAIN to false in the .env file, run the ansible playbook without doing anything. The website will be reachable under the bw cloud hostname.

Once you have added the DNS entries, the IT support has confirmed they have set up an alias or option C applies, configure the server by running:
```
cd ansible
ansible-playbook server_setup.yml --vault-password-file=.vault_pw
```
You can optionally update the project in the future by running:
```
ansible-playbook update_project.yml --vault-password-file=.vault_pw
```
"""

    md = Markdown(MARKDOWN)
    console.rule("")
    console.print(md)
    console.rule("")
    console.print("Bye :smiley:")
