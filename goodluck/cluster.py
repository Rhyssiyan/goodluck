import requests

def get_free_gpu(gpu_infos):
    """Determine which gpus are free in the current node

    :param gpu_info:
    :return:
    """
    free_gpus = []
    for gpu in gpu_infos:
        if len(gpu['processes']) == 0:
            free_gpus.append(int(gpu['index']))
    return free_gpus

class ClusterViewer:

    def __init__(self):
        self.node_gpu_info = {}
        self.update()

    def update(self):
        content = requests.get(f"http://10.19.124.11:8899/gpu?id=0").json()  # get gpu info for all nodes
        for info in content:
            name = info['hostname'].replace('compute1','').replace('node','')#leave node no. str
            free_gpus = get_free_gpu(info['gpus'])
            self.node_gpu_info[name] = free_gpus


    @property
    def n_free_gpus(self):
        return sum([len(node) for node in self.node_gpu_info])

