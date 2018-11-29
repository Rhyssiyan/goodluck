import os
import copy
import time
import sys

def get_free_gpu(node_gpu_info, banned_gpus, gpumem=4, card='all'):
    """Determine which gpus are free in the current node

    :param gpu_info:
    :return:
    """
    free_gpu_memory = lambda gpu: (gpu['memory.total']-gpu['memory.used'])/1024

    free_gpus = []
    for gpu in node_gpu_info:
        gpu_index = int(gpu['index'])
        if card.lower()!='all' and card not in gpu['name']:
            continue
        if gpu_index in banned_gpus:
            continue
        if len(gpu['processes']) > 0:
            continue
        if free_gpu_memory(gpu) < gpumem:
            continue
        free_gpus.append(gpu_index)

    return free_gpus


class Allocator:

    def __init__(self, permission, logger):
        self.banned_node_gpus = {}
        self.permission = permission
        self.logger = logger

    def get_nodes_gpuinfo(self, node_gpu_infos, gpumem, card):

        free_node_gpu_info = {}
        for nodename, node_gpu_info in node_gpu_infos.items():
            if nodename not in self.permission:
                continue
            banned_gpus = self.banned_node_gpus.get(nodename, [])
            free_node_gpu_info[nodename] = get_free_gpu(node_gpu_info, banned_gpus, gpumem, card)
        return free_node_gpu_info

    def allocate_node(self, ngpu, node_gpu_infos, gpumem, card):
        """

        Args:
            ngpu:
            node_gpu_info: {node: free_gpus} such as 1: [0,1,2,3]
            gpumem:
        Returns:
            free_nodes: dict node_i: free_gpus such as 01: 0,1,2,3
        """
        allocated_node = -1
        node_with_max_gpu, max_n_gpu = -1, 0
        allocated_gpus = []
        free_nodes = {}

        node_gpu_info = self.get_nodes_gpuinfo(node_gpu_infos, gpumem, card)


        for i, [nodei, free_gpus] in enumerate(node_gpu_info.items()):
            if len(free_gpus) >= ngpu:
                allocated_node = nodei
                allocated_gpus = free_gpus[:ngpu]
                free_nodes[nodei] = free_gpus

            if len(free_gpus) > max_n_gpu:
                max_n_gpu = len(free_gpus)
                node_with_max_gpu = nodei

        if max_n_gpu >= ngpu:
            allocated_node = node_with_max_gpu

        if allocated_node not in self.banned_node_gpus:
            self.banned_node_gpus[allocated_node] = []
            self.banned_node_gpus[allocated_node].extend(allocated_gpus)
        return allocated_node, allocated_gpus, free_nodes, node_with_max_gpu, max_n_gpu

    def allocate(self, ngpu, node_gpu_infos, gpumem, card='all', wait=False, vv=False):

        while True:
            node, gpu_idxs, free_nodes, node_with_max_gpu, max_n_gpu = self.allocate_node(ngpu, node_gpu_infos, gpumem, card)
            if vv:
                self.logger.vvinfo(node, gpu_idxs, free_nodes)
            if node!=-1:
                return node, gpu_idxs
            else:
                print(f"Now, the node with max free gpu is node{node_with_max_gpu} having {max_n_gpu}gpu")
            if not wait:
                sys.exit(1)
            print(f"Cluster is busy. There are no node having {ngpu} cards. Wait!")
            time.sleep(60)

