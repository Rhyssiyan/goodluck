import requests




class ClusterViewer:
    def __init__(self):
        self.node_gpu_info = {}

    def update(self):
        content = requests.get(f"http://10.19.124.11:8899/gpu?id=0").json()  # get gpu info for all nodes
        for info in content:
            name = info['hostname'].replace('compute1','').replace('node','')#leave node no. str
            self.node_gpu_info[name] = info['gpus']


    @property
    def n_free_gpus(self):
        return sum([len(node) for node in self.node_gpu_info])

