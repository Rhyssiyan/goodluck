#!/usr/bin/env python
import fire
import os
import yaml
import libtmux
import time
from datetime import datetime
from colorama import Fore, Back, Style
import locale
import sys

from goodluck.user import UserInfo
from goodluck.cluster import AIClusterViewer, P40ClusterViewer
from goodluck.allocator import Allocator
from goodluck.utils import get_session, Colorblock, LuckLogger, Commander, install_requirements, restore_locale,log_with_color
from goodluck.text import chinese_log

CARD_TYPE_LIST = ['ALL', '1080', 'M40', 'TITAN X', 'TITAN V', 'K', 'V100', 'P40']
CARD_SET = {'1080', 'M40', 'TITAN X', 'TITAN V', 'K', 'V100', 'P40'}
CARD_MAPPING = {
    'all': 'ALL',
    'v': 'TITAN V',
    'v100': 'V100',
    'm': 'M40',
    '1080': '1080',
    'k': 'K',
    'xp': 'TITAN X',
    'p40': 'P40',
}

def check_and_convert_card(cards):
    if isinstance(cards, str):
        cards = cards.split(',')
    elif isinstance(cards, int):
        cards = [str(cards)]
    legal_cards = set()
    for c in cards:
        c = str(c)
        if c.startswith('-'):
            c = CARD_MAPPING[c[1:]]
            legal_cards -= set([c])
        else:
            if c == 'all':
                tmp_card_set = CARD_SET
            else:
                c = CARD_MAPPING[c]
                tmp_card_set = set([c])
            assert c.upper() in CARD_TYPE_LIST, "Please check your card type input. \n \
                            Legal inputs are 'all' | '1080' | 'm' | 'xp' | 'v' | 'k' | 'v100' | 'p40'"
            legal_cards |= tmp_card_set

    return legal_cards

class Luck:
    def __init__(self):
        self.userinfo = UserInfo()
        self.clusterviewr = AIClusterViewer()
        self.logger = LuckLogger(self.userinfo)
        self.allocator = Allocator(self.userinfo.permission, self.logger)

        install_requirements()

        # chinese_log()
        self.v = False
        self.vv = False

    def get_allocated_node(self, ngpu=1, env=None, gpumem=4, card=CARD_SET, wait=False, specified_node=None):
        while True:
            self.clusterviewr.update()
            node, gpu_idxs = self.allocator.allocate(ngpu, self.clusterviewr.node_gpu_info, gpumem, card, self.vv,
                                                     specified_node)
            if node==-1:
                if not wait:
                    sys.exit(1)
                print(f"Cluster is busy. There are no node having {ngpu} cards. Wait!")
                time.sleep(3)
            else:

                return node, gpu_idxs

    def get_command(self, user_cmd, ngpu=1, env=None, exit=True, gpumem=4, card=CARD_SET, wait=False, virt_env=False, specified_node=None):

        node, gpu_idxs = self.get_allocated_node(ngpu, env, gpumem, card, wait, specified_node)
        command = Commander(node, gpu_idxs, user_cmd, env, exit, virt_env).get_ssh_command()
        if self.v:
            print("\nThe full command is:")
            log_with_color(command, Fore.YELLOW)
            print("")
        return command

    def run(self, user_cmd, ngpu=1, env=None, exit=False, gpumem=4, v=True, vv=True,
            card='all', wait=False, virt_env=False, node=None, force=False):
        """

        Args:
            user_cmd: The command you want to execute like "nvidia-smi" / "sh xx.sh"
            ngpu: how much gpu you want to use
            env: The environment name you want to source
            exit: Whether to exit the remote node terminal after program ends.
            gpumem: The minimum requirement of your program（Unit is GB)
            card: 'all' | '1080' | 'm' | 'xp' | 'v' | 'k' | 'v100' | 'p40'
                support 'all,-k'
            virt_env: If you use virtual env to manage your environment
            v: verbose mode
            vv: more verbose
            node: the node you specify to run. like 01,02,03,...
        Returns:

        """
        self.allocator.force = force

        node = str(node) if isinstance(node, int) else node
        assert not node or len(node)==2, "Node Format is wrong. Like 01, 02, ..., 34"
        card = check_and_convert_card(card)
        mapping = {
            'user_cmd': user_cmd,
            'ngpu': ngpu,
            'env': env,
            'exit': exit,
            'gpumem': gpumem,
            'card': card,
            'wait': wait,
            'virt_env': virt_env,
            'node': node,
            'v': v,
            'vv': vv,
            'force': force,
        }

        self.v = v
        self.vv = vv
        if self.v or self.vv:
            self.logger.vinfo(mapping)

        ssh_command = self.get_command(user_cmd, ngpu, env, exit, gpumem, card, wait, virt_env, node)

        #Tmux protection

        os.system(ssh_command)

    def run_yaml(self, cfg='./goodluck/test/default.yaml', name=None,  exit=True, wait=False, v=True, vv=True):
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
            ssh_command = self.get_command(**kwargs)
            pane.send_keys(ssh_command)

        if exit:
            print("The opened session will be closed.")
            time.sleep(5)
            server.kill_session(session_name)

    def watch(self, ngpu=1, gpumem=0, card=CARD_SET, noicon=False):
        if not noicon:
            chinese_log()
        card = check_and_convert_card(card)
        self.clusterviewr.update()
        node, gpu_idxs, free_nodes, node_with_max_gpu, max_n_gpu, total_gpus = self.allocator.allocate_node(ngpu, self.clusterviewr.node_gpu_info, gpumem, card)
        self.logger.watch_free_node_info(free_nodes, node_with_max_gpu, max_n_gpu, self.clusterviewr.nodes_gpu_type, total_gpus)

    def p40_watch(self, gpumem=0, card=CARD_SET, noicon=False):
        self.clusterviewr = P40ClusterViewer()
        self.watch(noicon=noicon)

    def wrap(self, cmd='', exit=False, env=None, virt_env=False):

        server = libtmux.Server()

        # Summarize cmd to get the session name
        cmd_name = cmd
        if ';' in cmd_name:
            cmd_name = cmd_name.split(';')[-1]
        else:
            cmd_name = cmd_name
        session_name = cmd_name.split(' ')[0] + '_' + datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        print(f"Session name: {session_name}")
        log_with_color(f"tmux attach -t {session_name}", fore=Fore.YELLOW)
        session = get_session(server, session_name)
        session.set_option("status", "off")

        pane = session.attached_pane

        if env:
            if virt_env:
                assert os.path.exists(env), "The virtual environment doesn't exist"
                pane.send_keys('source {self.env}')
            else:
                pane.send_keys(f"source activate {env}")

        if len(cmd)>0:
            python_cmd = f"""goodluck run_program '{cmd}' """
            pane.send_keys(python_cmd)

        if exit:
            pane.send_keys("exit")
        else:
            os.system(f"unset TMUX;tmux attach -t {session_name}")

    def run_program(self, cmd=''):
        chinese_log()
        # import pdb;pdb.set_trace()
        os.system(cmd)

if __name__ == '__main__':
    runner = Luck()
    fire.Fire(runner)
