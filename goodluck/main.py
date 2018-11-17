#!/usr/bin/env python
import fire
import os

from goodluck.cluster import ClusterViewer
from goodluck.utils import get_username, get_permission_info, allocate_node

class Runner:

    def __init__(self, node, gpu_idxs, user_cmd, env_name, exit):
        self.node = node
        self.gpu_idxs = gpu_idxs
        self.user_cmd = user_cmd
        self.env_name = env_name
        self.is_exit = exit
        self.cwd = os.getcwd()

    def get_command(self):
        command = f"source ~/.zshrc && cd {self.cwd}"

        if self.env_name:
            command += f" && source activate {self.env_name}"
        if len(self.gpu_idxs)>0:
            command += f" && export CUDA_VISIBLE_DEVICES=" + ",".join([str(idx) for idx in self.gpu_idxs])
        command += f" && {self.user_cmd}"
        if not self.is_exit:
            command += ";zsh"
        return command

    def run(self):
        command = self.get_command()
        ssh_command = f"ssh -t node{self.node} '{command}'"
        print(ssh_command)
        os.system(ssh_command)


class Luck:
    def __init__(self):
        self.user = get_username()
        self.nodes = get_permission_info(self.user)

        self.clusterviewr = ClusterViewer()


    def run(self, user_cmd, ngpu=1, env_name=None, exit=False):
        """
        :param ngpu:
        :param prog:
        :return:
        """
        self.clusterviewr.update()
        node, gpu_idxs = allocate_node(ngpu, self.clusterviewr.node_gpu_info)
        Runner(node, gpu_idxs, user_cmd, env_name, exit).run()



if __name__ == '__main__':
    runner = Luck()
    fire.Fire(runner)
