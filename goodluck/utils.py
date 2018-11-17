import platform
import requests

def get_username():
    return platform.node().strip().split('_')[0]


def get_permission_info(username):
    content = requests.get(f"http://10.19.124.11:8899/permission?username={username}").json()
    permissions = []
    for info in content['permission']:
        name = info['name']
        if 'node' in name:
            node = int(name[4:])
            permissions.append(node)

    return permissions






def allocate_node(ngpu, node_gpu_info):
    """

    :param ngpu:
    :param node_gpu_info: {node: free_gpus} such as 1: [0,1,2,3]
    :return:
    """

    for i, [nodei, free_gpus] in enumerate(node_gpu_info.items()):
        if len(free_gpus)>ngpu:
            return nodei, free_gpus[:ngpu]
