
import os
from loguru import logger
from cmdlinker.builtin.file_operation import FileOption
from cmdlinker.builtin.logger_operation import LoggerFormat


class CmdLinkerCliConf:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_cmd_cli_linker'):
            cls._cmd_cli_linker = super(CmdLinkerCliConf, cls).__new__(cls)
        return cls._cmd_cli_linker

    def __init__(self):
        self.base_path = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
        self.cmd_cli_conf = FileOption.read_yaml(os.path.join(self.base_path, "cli.yaml"))


if __name__ == '__main__':
    ...