import os
import sys
from colorama import Fore, Back, Style
import libtmux

def install_zh_cn():
    if not isinstance(os.system("which locale-gen"), list): #not installed
        os.system("apt-get update")
        os.system("apt-get install -y locales")
        os.system("locale-gen 'zh_CN.UTF-8'")
        os.system("update-locale LC_ALL='zh_CN.UTF-8'")

def restore_locale(sys_locale):
    os.system(f"update-locale LC_ALL='{sys_locale}' ")

class Colorblock:

    def __init__(self, fore=Fore.BLACK):
        self.fore = fore

    def __enter__(self):
        print(f"{self.fore}",end="")

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"{Style.RESET_ALL}")



def get_session(server, session_name):
    # Get session
    if not server.find_where({'session_name': session_name}):
        session = server.new_session(session_name=session_name)

    else:
        with Colorblock(Fore.RED):
            print("\nDon't support append window in existing session! Please change your session name.")
        sys.exit(1)
        # session = server.find_where({'session_name': session_name})
        # is_yes = input(prompt=f"{session_name} exists. Do you still want to append window on this session? Y(y)/N(n)")
        # assert is_yes.lower() in ['y', 'n']
        # if is_yes not in ['y', 'Y']:
        #     print("Please change your session name.")
    return session


class LuckLogger:

    def __init__(self, userinfo):
        self.userinfo = userinfo

    def vinfo(self):
        print(f"User:{self.userinfo.username}")
        print(f"Permission:{self.userinfo.permission}")

        # GPU Info
        # free memory
        # nproc

    def vvinfo(self, node, gpu_idxs, free_nodes):
        list_to_str = lambda lst: ",".join([str(item) for item in lst])
        gpu_idxs = list_to_str(gpu_idxs)
        free_nodes = list_to_str(free_nodes)
        print(f"Your program will run on gpu{Fore.MAGENTA}{gpu_idxs}{Style.RESET_ALL} of node{Fore.MAGENTA}{node}{Style.RESET_ALL}")
        print(f"The nodes that satisfy the requirement of your program are: ", end="")
        with Colorblock(fore=Fore.YELLOW):
            print(f"{free_nodes}")



class Commander:

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
            command += " ;zsh"
        return command

    def get_ssh_command(self):
        command = self.get_command()
        ssh_command = f"ssh -t node{self.node} '{command}'"
        print(ssh_command)
        return ssh_command