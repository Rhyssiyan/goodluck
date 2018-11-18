#!/usr/bin/env python
import fire
import os
import yaml
import libtmux
import time
from colorama import Fore, Back, Style
import locale
from goodluck.user import UserInfo
from goodluck.cluster import ClusterViewer
from goodluck.allocator import Allocator
from goodluck.utils import get_session, Colorblock, LuckLogger, Commander, install_zh_cn, restore_locale
from goodluck.text import chinese_log

CARD_TYPE_LIST = ['ALL', '1080', 'M40', 'TITAN X', 'TITAN V', 'K40', 'V100']

class Luck:
    def __init__(self):
        self.userinfo = UserInfo()
        self.clusterviewr = ClusterViewer()
        self.logger = LuckLogger(self.userinfo)
        self.allocator = Allocator(self.userinfo.permission, self.logger)
        self.v = False
        self.vv = False

        self.sys_locale = locale.getlocale()
        if self.sys_locale[0] and self.sys_locale[1]:
            self.sys_locale = self.sys_locale[0] + "." + self.sys_locale[1]
        else:
            self.sys_locale = None

        install_zh_cn()
        chinese_log()

        if not self.sys_locale:
            restore_locale(self.sys_locale)



    def get_ssh_command(self, user_cmd, ngpu=1, env=None, exit=False, gpumem=4, card='all', wait=False, virt_env=False):
        ngpu, card = int(ngpu), str(card)
        assert card.upper() in CARD_TYPE_LIST, "Please check your card type input. \n \
                                    Legal inputs are 'all' | '1080' | 'M40' | 'Titan X' | 'Titan V' | 'K40' | 'V100'"
        self.clusterviewr.update()
        node, gpu_idxs, free_nodes = self.allocator.allocate(ngpu, self.clusterviewr.node_gpu_info,
                                                             gpumem, card, wait, self.vv)

        return Commander(node, gpu_idxs, user_cmd, env, exit, virt_env).get_ssh_command()

    def run(self, user_cmd, ngpu=0, env=None, exit=False, gpumem=4, v=False, vv=False,
            card='all', wait=False, virt_env=False):
        """

        Args:
            user_cmd: The command you want to execute like "nvidia-smi" / "sh xx.sh"
            ngpu: how much gpu you want to use
            env: The environment name you want to source
            exit: Whether to exit the remote node terminal after program ends.
            gpumem: The minimum requirement of your program（Unit is GB)
            card: 'all' | '1080' | 'M40' | 'Titan X' | 'Titan V' | 'K40' | 'V100'
            virt_env: If you use virtual env to manage your environment
            v: verbose mode
            vv: more verbose
        Returns:

        """
        mapping = {
            'user_cmd': user_cmd,
            'ngpu': ngpu,
            'env': env,
            'exit': exit,
            'gpumem': gpumem,
            'card': card,
            'wait': wait,
            'virt_env': virt_env,
            'v': v,
            'vv': vv
        }

        self.v = v
        self.vv = vv
        if self.v or self.vv:
            self.logger.vinfo(mapping)

        ssh_command = self.get_ssh_command(user_cmd, ngpu, env, exit, gpumem, card, wait)
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
