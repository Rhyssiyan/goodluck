import platform
import requests

class UserInfo:

    def __init__(self):
        self.username = get_username()
        self.permission = get_permission_info(self.username)


def get_username():
    return platform.node().strip().split('-')[0]


def get_permission_info(username):
    content = requests.get(f"http://10.19.124.11:8899/permission?username={username}").json()
    permissions = []
    for info in content['permission']:
        name = info['name']
        if 'node' in name:
            node = name[4:]
            permissions.append(node)

    return permissions
