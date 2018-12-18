import os
import copy
import time
import sys

def get_gpus(node_gpu_info, banned_gpus, gpumem=4, card='all', free_flag=True):
    """Determine which gpus are free in the current node

    :param gpu_info:
    :return:
    """
    free_gpu_memory = lambda gpu: (gpu['memory.total']-gpu['memory.used'])/1024

    # free_gpus = [True for i in range(len(node_gpu_info))]
    free_gpus = []
    for gpu in node_gpu_info:
        gpu_index = int(gpu['index'])

        if card.lower()!='all' and card not in gpu['name']:
            continue
        if free_flag and gpu_index in banned_gpus:
            continue
        if free_flag and len(gpu['processes']) > 0:
            continue
        if free_flag and free_gpu_memory(gpu) < gpumem:
            continue
        free_gpus.append(gpu_index)

    return free_gpus



class Allocator:

    def __init__(self, permission, logger):
        self.banned_node_gpus = {}
        self.permission = permission
        self.logger = logger
        self.force = False

    def get_nodes_gpuinfo(self, node_gpu_infos, gpumem, card):

        free_node_gpu_info = {}
        total_qualified_gpu = 0
        for nodename, node_gpu_info in node_gpu_infos.items():
            if nodename not in self.permission:
                continue
            banned_gpus = self.banned_node_gpus.get(nodename, [])
            free_node_gpu_info[nodename] = get_gpus(node_gpu_info, banned_gpus, gpumem, card, True if not self.force else False)
            qualified_gpu =  len(get_gpus(node_gpu_info, banned_gpus, gpumem, card, False))
            total_qualified_gpu += qualified_gpu
        return free_node_gpu_info, total_qualified_gpu

    def allocate_node(self, ngpu, node_gpu_infos, gpumem, card, specified_node=None):
        """

        Args:
            ngpu:
            node_gpu_info: {node: free_gpus} such as 1: [0,1,2,3]
            gpumem:
            specified_node: specify which node to run
        Returns:
            free_nodes: dict node_i: free_gpus such as 01: 0,1,2,3
        """
        allocated_node = -1
        free_gpu_on_allocated_node = 32 #A large enough intial value
        node_with_max_gpu, max_n_gpu = -1, 0
        allocated_gpus = []
        free_nodes = {}

        node_gpu_info, total_qualified_gpu = self.get_nodes_gpuinfo(node_gpu_infos, gpumem, card)

        for i, [nodei, free_gpus] in enumerate(node_gpu_info.items()):
            if len(free_gpus) >= ngpu:
                if specified_node and specified_node==nodei:
                    allocated_node = nodei
                    allocated_gpus = free_gpus[:ngpu]
                    break

                if allocated_node == -1 or len(free_gpus) < free_gpu_on_allocated_node:
                    allocated_node = nodei
                    allocated_gpus = free_gpus[:ngpu]
                    free_gpu_on_allocated_node = len(free_gpus)
                free_nodes[nodei] = free_gpus

            if len(free_gpus) > max_n_gpu:
                max_n_gpu = len(free_gpus)
                node_with_max_gpu = nodei
        if specified_node and allocated_node != specified_node:
            print(f"The node is not satisfied your requirement ")
            sys.exit(0)

        if allocated_node not in self.banned_node_gpus:
            self.banned_node_gpus[allocated_node] = []
            self.banned_node_gpus[allocated_node].extend(allocated_gpus)
        return allocated_node, allocated_gpus, free_nodes, node_with_max_gpu, max_n_gpu, total_qualified_gpu

    def allocate(self, ngpu, node_gpu_infos, gpumem, card='all', vv=False, specified_node=None):
        node, gpu_idxs, free_nodes, node_with_max_gpu, max_n_gpu, _  = self.allocate_node(ngpu, node_gpu_infos, gpumem, card, specified_node)

        if vv:
            self.logger.vvinfo(node, gpu_idxs, free_nodes)
        if node==-1:
            print(f"Now, the node with max free gpu is node{node_with_max_gpu} having {max_n_gpu}gpu")
            return -1, None
        else:
            return node, gpu_idxs

