from goodluck.utils import Colorblock, log_with_color
from colorama import Fore, Back, Style
import random

def chinese_log():
    val = random.random()
    if val < 0.25:
        log_with_color("")
        log_with_color('\t--------------------------------------------', fore=Fore.RED, style=Style.BRIGHT)
        log_with_color('\t多发paper共建和谐社会, 文明用卡方便你我他!!!', fore=Fore.RED, style=Style.BRIGHT)
        log_with_color('\t多发paper共建和谐社会, 文明用卡方便你我他!!!', fore=Fore.RED, style=Style.BRIGHT)
        log_with_color('\t多发paper共建和谐社会, 文明用卡方便你我他!!!', fore=Fore.RED, style=Style.BRIGHT)
        log_with_color('\t--------------------------------------------', fore=Fore.RED, style=Style.BRIGHT)
        log_with_color('\n')
    else:
        log_with_color(r"""
                         _ooOoo_
                        o8888888o
                        88" . "88
                        (| -_- |)
                         O\ = /O
                     ____/`---'\____
                   .   ' \\| |// `.
                    / \\||| : |||// \
                  / _||||| -:- |||||- \
                    | | \\\ - /// | |
                  | \_| ''\---/'' | |
                   \ .-\__ `-` ___/-. /
                ___`. .' /--.--\ `. . __
             ."" '< `.___\_<|>_/___.' >'"".
            | | : `- \`.;`\ _ /`;.`/ - ` : | |
              \ \ `-. \_ __\ /__ _/ .-` / /
      ======`-.____`-.___\_____/___.-`____.-'======""", fore=Fore.YELLOW)

        log_with_color("\t\t    佛祖保佑 永无bug", fore=Fore.GREEN)
        log_with_color("\n")

