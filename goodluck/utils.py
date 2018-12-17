import os
import sys
from colorama import Fore, Back, Style
import libtmux
from pprint import pprint
import inspect

def install_requirements():
    install_ascii_packages()
    install_zh_cn()

def install_ascii_packages():
    if os.system("which cowsay > /dev/null")!=0:
        os.system("apt-get install -y cowsay")

def install_zh_cn():
    if os.system("which locale-gen > /dev/null")!=0: #not installed
        os.system("apt-get update")
        os.system("apt-get install -y locales")
        os.system("locale-gen 'zh_CN.UTF-8'")
        os.system("update-locale LC_ALL='zh_CN.UTF-8'")
        os.system("source ~/.zshrc")


def restore_locale(sys_locale):
    os.system(f"update-locale LC_ALL='{sys_locale}' ")

class Colorblock:

    def __init__(self, fore=Fore.BLACK):
        self.fore = fore

    def __enter__(self):
        print(f"{self.fore}",end="")

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"{Style.RESET_ALL}")


def log_with_color(text, fore=Fore.BLACK, style=Style.NORMAL, end="\n"):
    print(f"{fore}{style}{text}{Style.RESET_ALL}", end=end)

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

    def vinfo(self, mapping):
        print("The config for current run:")
        pprint(mapping)
        print("----------------------------")
        print("")

        print(f"User: {Fore.MAGENTA}{self.userinfo.username}{Style.RESET_ALL}")
        print(f"Permission: {Fore.MAGENTA}{self.userinfo.permission}{Style.RESET_ALL}")

        # GPU Info
        # free memory
        # nproc

    def vvinfo(self, node, gpu_idxs, free_nodes):
        if node==-1:
            return
        list_to_str = lambda lst: ",".join([str(item) for item in lst])
        gpu_idxs = list_to_str(gpu_idxs)
        free_nodes = list_to_str(free_nodes)
        print("")
        print(f"Your program will run on gpu{Fore.YELLOW}{gpu_idxs}{Style.RESET_ALL} of node{Fore.YELLOW}{node}{Style.RESET_ALL}")
        print(f"The nodes that satisfy the requirement of your program are: ", end="")
        log_with_color(free_nodes, Fore.YELLOW)

    def watch_free_node_info(self, free_nodes, node_with_max_gpu, max_n_gpu, nodes_gpu_type, total_gpus):
        list_to_str = lambda lst: ",".join([str(item) for item in lst])
        free_node_list = list_to_str(free_nodes.keys())

        print(f"There are {Fore.GREEN}{len(free_nodes)}{Style.RESET_ALL} free nodes in total.")
        print(f"There are {Fore.GREEN}{sum([len(gpus) for gpus in free_nodes.values()])}/{total_gpus}{Style.RESET_ALL} free gpus in total.")

        print(f"\nFree node list: ", end="")
        log_with_color(free_node_list, Fore.YELLOW)
        print("")

        for nodei, free_gpus in free_nodes.items():
            free_gpus = list_to_str(free_gpus)
            print(f"For node{nodei}: free gpus are ", end="")
            log_with_color(nodes_gpu_type[nodei], Fore.GREEN, end="")
            log_with_color(", " + free_gpus, Fore.CYAN)


        print(f"\nNow, the node with max free gpu is node{node_with_max_gpu} having {max_n_gpu} gpu")

class Commander:

    def __init__(self, node, gpu_idxs, user_cmd, env_name, exit, virt_env):
        self.node = node
        self.gpu_idxs = gpu_idxs
        self.user_cmd = user_cmd
        self.env_name = env_name
        self.is_exit = exit
        self.virt_env = virt_env # Use virtual env if True else conda
        self.cwd = os.getcwd()

    def get_command(self):
        command = f"source ~/.zshrc && cd {self.cwd}"

        if self.env_name:
            if self.virt_env:
                assert os.path.exists(self.env_name), "The virtual environment doesn't exist"
                command += f" && source {self.env_name}"
            else:
                command += f" && source activate {self.env_name}"
        if len(self.gpu_idxs)>0:
            command += f" && export CUDA_VISIBLE_DEVICES=" + ",".join([str(idx) for idx in self.gpu_idxs])
        command += f" && {self.user_cmd}"
        if not self.is_exit:
            command += " ;zsh"
        return command

    def get_ssh_command(self):
        """ssh command to make command run on specified node

                Returns:

                """
        command = self.get_command()
        ssh_command = f"ssh -t node{self.node} '{command}'"
        return ssh_command

