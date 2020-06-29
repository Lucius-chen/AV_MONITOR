# -*- coding: utf-8 -*-
# @Author  : lucius
# @Email   : cnotperfect@foxmail.com

"""通用类和函数。"""

from difflib import Differ
import os
import sys
try:
    from threading import _Timer as Timer
except ImportError:
    from threading import Timer



class RepeatingTimer(Timer):
    '''重复计数器https://gist.github.com/alexbw/1187132#gistcomment-1408433'''
    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()


# https://stackoverflow.com/a/10775310
def highlight_changes(s1, s2):
    """Highlight words that are changed."""
    # pylint: disable=invalid-name
    l1 = s1.split(' ')
    l2 = s2.split(' ')
    dif = list(Differ().compare(l1, l2))
    return " ".join(["\033[1m" + i[2:] + "\033[0m" if i[:1] == "+" else i[2:]
                     for i in dif if not i[:1] in "-?"])


def restart_program():
    """重新启动当前程序。"""
    python = sys.executable            # 获取解析器路径
    os.execl(python, python, *sys.argv)#重启
