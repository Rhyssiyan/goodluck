import os
import copy

def get_free_gpu(node_gpu_info, banned_gpus, min_gpu_mem=8, card_type='all'):
    """Determine which gpus are free in the current node

    :param gpu_info:
    :return:
    """
    free_gpu_memory = lambda gpu: (gpu['memory.total']-gpu['memory.used'])/1024

    free_gpus = []
    for gpu in node_gpu_info:
        gpu_index = int(gpu['index'])
        if gpu_index in banned_gpus:
            continue
        if len(gpu['processes']) > 0:
            continue
        if free_gpu_memory(gpu) < min_gpu_mem:
            continue
        if card_type!='all' and all([card_type not in gpu['name']]):
            continue

        free_gpus.append(gpu_index)

    return free_gpus

class Allocator:


    def __init__(self, permission):
        self.banned_node_gpus = {}
        self.permission = permission

    def get_nodes_gpuinfo(self, node_gpu_infos, min_gpu_mem, card_type='all'):

        free_node_gpu_info = {}
        for nodename, node_gpu_info in node_gpu_infos.items():
            if nodename not in self.permission:
                continue
            banned_gpus = self.banned_node_gpus.get(nodename, [])
            free_node_gpu_info[nodename] = get_free_gpu(node_gpu_info, banned_gpus, min_gpu_mem, card_type)
        return free_node_gpu_info

    def allocate_node(self, ngpu, node_gpu_infos, min_gpu_mem, card_type='all'):
        """

        Args:
            ngpu:
            node_gpu_info: {node: free_gpus} such as 1: [0,1,2,3]
            min_gpu_mem:
        Returns:

        """
        allocated_node = -1
        allocated_gpus = []
        free_nodes = []
        node_gpu_info = self.get_nodes_gpuinfo(node_gpu_infos, min_gpu_mem, card_type='all')
        for i, [nodei, free_gpus] in enumerate(node_gpu_info.items()):
            if len(free_gpus) > ngpu:
                allocated_node = nodei
                allocated_gpus = free_gpus[:ngpu]
                free_nodes.append(nodei)

        if allocated_node not in self.banned_node_gpus:
            self.banned_node_gpus[allocated_node] = []
        self.banned_node_gpus[allocated_node].extend(allocated_gpus)

        return allocated_node, allocated_gpus, free_nodes

    def allocate(self, ngpu, node_gpu_infos, min_gpu_mem, card_type='all', wait=False):

        while True:
            node, gpu_idxs, free_nodes = self.allocate_node(ngpu, node_gpu_infos, min_gpu_mem, card_type)

            if node!=-1:
                return node, gpu_idxs, free_nodes
            print("Cluster is busy. There are no node. Still searching.")
            time.sleep(60)