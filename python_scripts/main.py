from helpers import get_auth_token, generate_cloud_config
import requests

token = get_auth_token()

###################################################


res = requests.get("https://api01.ma.bw-cloud.org:9292/v2/images",
                   headers={'content-type': 'application/json',
                            'X-Auth-Token': token
                            },
                   )


data = res.json()["images"]
image_id = next(item for item in data if item["name"] == "Ubuntu 20.04")["id"]

###################################################

res = requests.get('https://api01.ma.bw-cloud.org:8774/v2.1/flavors',
                   headers={'content-type': 'application/json',
                            'X-Auth-Token': token
                            },
                   )

data = res.json()["flavors"]
flavor_id = next(item for item in data if item["name"] == "m1.tiny")["id"]

###################################################


def create_sec_group_rule(direction, protocol, security_group_id):

    json = {
        "security_group_rule": {
            "direction": direction,
            "port_range_min": "1",
            "ethertype": "IPv4",
            "port_range_max": "65535",  # highest possible port number
            "protocol": protocol,
            "security_group_id": security_group_id
        }
    }

    requests.post('https://api01.ma.bw-cloud.org:9696//v2.0/security-group-rules',
                  headers={'content-type': 'application/json',
                           'X-Auth-Token': token,
                           },
                  json=json
                  )


res = requests.get('https://api01.ma.bw-cloud.org:9696/v2.0/security-groups',
                   headers={'content-type': 'application/json',
                            'X-Auth-Token': token
                            },
                   )

data = res.json()["security_groups"]

Found = next((item for item in data if item["name"] == "allow_everything"), None)

if Found is None:

    json2 = {
        "security_group": {
            "name": "allow_everything",
            "description": "This security group will allow all in- and outbund conections.\
             This is very insecure.\
             Only use it when you plan to configure a firewall on the server itself.",
        }
    }

    res2 = requests.post('https://api01.ma.bw-cloud.org:9696/v2.0/security-groups',
                         headers={'content-type': 'application/json',
                                  'X-Auth-Token': token,
                                  },
                         json=json2
                         )

    security_group_id = res2.json()["security_group"]["id"]

    create_sec_group_rule("ingress", "udp", security_group_id)
    create_sec_group_rule("egress", "udp", security_group_id)
    create_sec_group_rule("ingress", "tcp", security_group_id)
    create_sec_group_rule("egress", "tcp",  security_group_id)

else:
    print("security group already exists")


###################################################

json = {
    "server": {
                "name": "test",
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

print(res.text)
