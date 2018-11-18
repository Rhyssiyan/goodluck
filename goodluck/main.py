#!/usr/bin/env python
import fire
import os
import yaml
import libtmux
import time
from colorama import Fore, Back, Style

from goodluck.user import UserInfo
from goodluck.cluster import ClusterViewer
from goodluck.allocator import Allocator
from goodluck.utils import get_session, Colorblock, LuckLogger, Commander

CARD_TYPE_LIST = ['ALL', 'GTX 1080', 'M40', 'TITAN X', 'TITAN V', 'K40', 'V100']

class Luck:
    def __init__(self):
        self.userinfo = UserInfo()
        self.clusterviewr = ClusterViewer()
        self.allocator = Allocator()
        self.v = False
        self.vv = False
        with Colorblock(Fore.RED) as color:
            print('\t------------------------------------------')
            print('\t多发paper共建和谐社会, 文明用卡方便你我他!!!')
            print('\t多发paper共建和谐社会, 文明用卡方便你我他!!!')
            print('\t多发paper共建和谐社会, 文明用卡方便你我他!!!')
            print('\t------------------------------------------')
            print('\n')
        self.logger = LuckLogger(self.userinfo)

    def get_ssh_command(self, user_cmd, ngpu=1, env=None, exit=False, min_gpu_mem=8, card_type='all', wait=False):
        ngpu = int(ngpu)
        assert card_type.upper() in CARD_TYPE_LIST, "Please check your card type input. \n \
                                    Legal inputs are 'all' | 'GTX 1080' | 'M40' | 'Titan X' | 'Titan V' | 'K40' | 'V100'"
        self.clusterviewr.update()
        node, gpu_idxs, free_nodes = self.allocator.allocate(ngpu, self.clusterviewr.node_gpu_info,
                                                             min_gpu_mem, card_type, wait)
        # import pdb;pdb.set_trace()
        if self.vv:
            self.logger.vvinfo(node, gpu_idxs, free_nodes)
        return Commander(node, gpu_idxs, user_cmd, env, exit).get_ssh_command()

    def run(self, user_cmd, ngpu=1, env=None, exit=False, min_gpu_mem=8, v=False, vv=False, card_type='all', wait=False):
        """

        Args:
            user_cmd: The command you want to execute like "nvidia-smi" / "sh xx.sh"
            ngpu: how much gpu you want to use
            env: The environment name you want to source
            exit: Whether to exit the remote node terminal after program ends.
            min_gpu_mem: The minimum requirement of your program（Unit is GB)
            card_type: 'all' | 'GTX 1080' | 'M40' | 'Titan X' | 'Titan V' | 'K40' | 'V100'
            v: verbose mode

        Returns:

        """
        self.v = v
        self.vv = vv
        if self.v or self.vv:
            self.logger.vinfo()

        ssh_command = self.get_ssh_command(user_cmd, ngpu, env, exit, min_gpu_mem, card_type, wait)
        os.system(ssh_command)

    def run_yaml(self, cfg='./goodluck/test/default.yaml', name=None, v=False, exit=False, wait=False, vv=False):
        self.v = v
        self.vv = vv
        if self.v or self.vv:
            self.logger.vinfo()

        assert os.path.exists(cfg), "The configuration doesn't exist"
        with open(cfg) as f:
            exp_dict = yaml.load(f)

        session_name = name if name else cfg.split('/')[-1].replace('.', '_')

        server = libtmux.Server()
        # import pdb;pdb.set_trace()
        session = get_session(server, session_name)


        for i, (exp_name, kwargs) in enumerate(exp_dict.items()):
            if i==0:
                session.attached_window.rename_window(exp_name) #Rename the name of window 0
            else:
                window = session.new_window(attach=True, window_name=exp_name)
            pane = session.attached_pane
            ssh_command = self.get_ssh_command(**kwargs)
            pane.send_keys(ssh_command)


        if exit:
            print("The opened session will be closed.")
            time.sleep(5)
            server.kill_session(session_name)



if __name__ == '__main__':
    runner = Luck()
    fire.Fire(runner)
