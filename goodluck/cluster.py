import requests


class ClusterViewer:
    def __init__(self):
        self.node_gpu_info = {}
        self.nodes_gpu_type = {}
        self.update_gpu_type()

    def update_gpu_type(self):
        content = requests.get(f"http://10.15.89.41:8899/{self.gpu_page}?id=0").json()  # get gpu info for all nodes
        for info in content:
            name = info['hostname'].replace(self.node_prefix, '').replace('node', '')  # leave node no. str
            self.nodes_gpu_type[name] = info['gpus'][0]['name'] #Get gpu type such as titan xp

    def update(self):

        content = requests.get(f"http://10.15.89.41:8899/{self.gpu_page}?id=0").json()  # get gpu info for all nodes
        for info in content:
            name = info['hostname'].replace(self.node_prefix,'').replace('node','')#leave node no. str
            self.node_gpu_info[name] = info['gpus']
        pause = 1

    @property
    def n_free_gpus(self):
        return sum([len(node) for node in self.node_gpu_info])


class AIClusterViewer(ClusterViewer):

    def __init__(self):
        self.node_prefix = "compute1"
        self.gpu_page = "gpu"
        super(AIClusterViewer, self).__init__()



class P40ClusterViewer(ClusterViewer):

    def __init__(self):
        self.node_prefix = "sist-gpu"
        self.gpu_page = "p40_gpu"
        super(P40ClusterViewer, self).__init__()


