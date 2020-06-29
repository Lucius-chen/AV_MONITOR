# -*- coding: utf-8 -*-
# @Author  : lucius
# @Email   : cnotperfect@foxmail.com

"""Configuration-related classes and functions."""

# pylint: disable=import-error
from pathlib import Path
import argparse
import logging
import logging.config
import os
from six.moves import configparser
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from auxiliary import utils

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def parse_command_line_args():
    """
    定义和解析命令行选项。
    :return args -> <class 'argparse.Namespace'>  Namespace(loglevel=20)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--debug",
        help="启用debug日志级别",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO,
    )
    args = parser.parse_args()
    # print(args)
    return args


def setup_logging(loglevel):
    """日志配置"""
    # print(loglevel)
    logging_config = dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            'f': {
                'format':
                    "%(asctime)s %(levelname)s %(name)s - %(message)s",
                'datefmt': "%F %T"}},
        handlers={
            'h': {
                'class': "logging.StreamHandler",
                'formatter': "f",
                'level': loglevel}},
        root={
            'handlers': ["h"],
            'level': loglevel},
    )
    logging.config.dictConfig(logging_config)


class Configs(object):
    """处理配置文件"""

    def __init__(self, title):
        # APP配置路径
        # print(os.environ)
        if 'LOCALAPPDATA' in os.environ:
            self.app_config_path = Path(os.environ['LOCALAPPDATA']) / title
        elif 'XDG_CONFIG_HOME' in os.environ:
            self.app_config_path = Path(os.environ['XDG_CONFIG_HOME']) / title
        else:
            self.app_config_path = Path(os.environ['HOME']) / ".config" / title
        logger.info("Config path: {}".format(self.app_config_path))

        # 从default_settings.ini和settings.ini加载和合并选项。
        self.settings = MyConfigParser()
        script_path = Path(__file__).parent # 默认配置路径
        defaults_file = script_path / "default_settings.ini"
        try:
            self.settings.read_file(defaults_file.open())
        except AttributeError:
            self.settings.readfp(defaults_file.open())  # deprecated
        self.settings_file = self.app_config_path / "settings.ini"
        self.settings.read(str(self.settings_file))

        # 不存在就创建 settings.ini
        if not self.settings_file.is_file():
            # self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            self.settings_file.parent.mkdir(parents=True)
            with self.settings_file.open('w') as configfile:
                self.settings.write(configfile)

        # 加载 state.ini 用于记录程序状态
        self.state_file = self.app_config_path / "state.ini"
        print(self.state_file)
        self.state = MyConfigParser()
        self.state.read(str(self.state_file))

        # 使用watchdog监控文件系统事件
        path = self.app_config_path
        event_handler = MyWatchdogHandler(patterns=[str(self.settings_file)])
        observer = Observer()
        observer.schedule(event_handler, str(path), recursive=False)
        observer.start()

    def load_state_value(self, section, option):
        """从state.ini读取值"""
        # print(self.state.keys())
        # try:
        logger.debug("Loading state [{}] {}".format(section, option))
        return self.state.get(section, option)
        # except (configparser.NoSectionError, configparser.NoOptionError):
        #     raise ValueError("State not saved or invalid.")

    def save_state_value(self, section, option, value):
        """Save value to state."""
        logger.debug("Saving state [{}] {}: {}".format(section, option, value))
        if not self.state.has_section(section):
            logger.debug("Adding section [{}] to state".format(section))
            self.state.add_section(section)
        self.state.set(section, option, value)
        with self.state_file.open('w') as configfile:
            self.state.write(configfile)


class MyConfigParser(configparser.ConfigParser):
    """重写ConfigParser添加了俩个方法"""

    # pylint: disable=too-many-ancestors, no-member

    def getmultifloat(self, section, option):
        """
        :param section:
        :param option:
        :return: 逗号分隔的浮点数列表
        """
        value = self.get(section, option)
        return [float(x) for x in value.replace(" ", "").split(",")]

    def getmultistr(self, section, option):
        """
        :param section: 
        :param option: 
        :return: 逗号分隔的字符串列表
        """""
        value = self.get(section, option)
        return [str(x) for x in value.replace(" ", "").split(",")]


class MyWatchdogHandler(PatternMatchingEventHandler):
    """
    如果传入模式与相关文件路径匹配，则触发程序重新启动与发生的事件
    """
    ignore_directories = True

    def on_any_event(self, event):
        logger.info("Restarting...")
        utils.restart_program()
