from loguru import logger
from typing import Union, Text
from cmdlinker.builtin.exception import CmdLinkerMutexException, CmdLinkerMulMutexException
from cmdlinker.builtin.ssh_utils import SSHClient
from cmdlinker.builtin.shell_utils import ShellClient


class Cmds:
    def __init__(self):
        self.index = 0
        self.CMD_LIST = []


class Runner:

    def __init__(self):
        self._mutexs = []
        self._gcs = []
        self._not_mutexs = []
        self.pre: Runner = object
        self.root: Runner = object
        self.next: Union[Runner] = object
        self.main_cmd: Text = None
        self.cmds: Cmds = None
        self.ssh_client: SSHClient = None
        self.sudo: bool = True
        self.timeout: int = 20

    def _exclude(self, cmd_obj):
        if not cmd_obj.mark:
            logger.debug(f"命令对象：{cmd_obj.__class__.__name__}未被使用")
            return False
        else:
            return True

    def _get_execute_cmd(self, cmd_obj):
        if cmd_obj.need_value:
            return f"{cmd_obj.meta_data['original_cmd']} {cmd_obj.value}"
        else:
            return f"{cmd_obj.meta_data['original_cmd']}"

    def _get_log_desc(self):
        if self.pre == self.root:
            log_desc = "子"
        elif self.pre is None and self.root == self:
            log_desc = "根"
        else:
            log_desc = "父"
        return log_desc

    def cmd_checker(self):
        log_desc = self._get_log_desc()
        logger.info("==" * 20 + f"开启{log_desc}命令{self.__class__.__name__}合法性检查" + "==" * 20)
        for cmd_obj_str in vars(self).keys():
            cmd_obj = getattr(self, cmd_obj_str)
            if isinstance(cmd_obj, BaseCmd):
                if cmd_obj_str == "next":
                    continue
                if not self._exclude(cmd_obj):
                    continue
                if cmd_obj.mutex:
                    self._mutexs.append(cmd_obj)
                    logger.debug(f"{self.main_cmd}添加互斥对象：{cmd_obj},最新互斥对象列表：")
                else:
                    self._not_mutexs.append(cmd_obj)
                    logger.debug(f"{self.main_cmd}添加非互斥对象：{cmd_obj},最新非互斥对象列表：{self._not_mutexs}")
        if len(self._mutexs) > 1:
            raise CmdLinkerMulMutexException(self.__class__.__name__, self._mutexs)
        if len(self._mutexs) != 0 and len(self._not_mutexs) != 0:
            raise CmdLinkerMutexException(self.__class__.__name__, self._mutexs, self._not_mutexs)
        if self.pre == self.root:
            logger.debug(f"启用命令对象{self.__class__.__name__} 根命令: {self.root.__class__.__name__} 检查")
            self.pre.cmd_checker()
        elif self.pre is None and self.root == self:
            pass
        else:
            logger.debug(f"启用命令对象{self.__class__.__name__}父命令: {self.pre.__class__.__name__} 检查")
            self.pre.cmd_checker()
        self._not_mutexs = []
        self._mutexs = []
        logger.info("==" * 20 + f"{log_desc}命令{self.__class__.__name__}合法性检查通过" + "==" * 20)

    def runner(self):
        self.cmd_checker()
        cmd = self.exec_cmd()
        self.cmds.CMD_LIST = []
        return self.ssh_client.run_cmd(cmd, timeout=self.timeout)

    def collector(self):
        return self.cmds.CMD_LIST.sort(key=lambda cmd_obj: cmd_obj.index)

    def exec_cmd(self):
        self.cmds.CMD_LIST.sort(key=lambda cmd_obj: cmd_obj.index)
        cmd_list = [self.main_cmd] + [self._get_execute_cmd(cmd) for cmd in self.cmds.CMD_LIST]
        if self.sudo:
            cmd_list.insert(0, "sudo")
        logger.info(f"执行命令列表：{cmd_list}")
        cmd = " ".join(cmd_list)
        return cmd


class BaseCmd(Runner):
    def __init__(self):
        super().__init__()
        self.cmds: Cmds = None
        self.meta_data = None
        self.mutex = None
        self.need_value = None
        self.has_child_cmd = None
        self.gc = None
        self.child_cmd = None
        self.default_value = None
        self.value = None
        self.mark = None
        self.index = None
        self.level = 0
        self._mutexs = []
        self._gcs = []
        self._not_mutexs = []
        self.main_cmd = "docker"
        self.pre: object = object
        self.root: object = object
        self.next: Union[object] = object
        self.ssh_client: SSHClient = None


class Ps(BaseCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Docker = pre_obj
        self.root: Docker = root_obj
        self.next: Union[Ps] = self
        self.meta_data = {'mapping_name': 'ps', 'original_cmd': 'ps', 'value': False, 'mutex': False, 'default': 'None',
                          'has_child_cmd': False, 'child_cmds': [], 'parent_cmd': 'Docker', 'root_cmd': 'Docker'}
        self.level = 2
        self.mutex = False
        self.need_value = False
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False

        self.default_value = "None"
        self.value = self.default_value
        self.mark = False


class Inspect(BaseCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Docker = pre_obj
        self.root: Docker = root_obj
        self.next: Union[Inspect] = self
        self.meta_data = {'mapping_name': 'inspect', 'original_cmd': 'inspect', 'value': True, 'mutex': False,
                          'default': 'None', 'has_child_cmd': False, 'child_cmds': [], 'parent_cmd': 'Docker',
                          'root_cmd': 'Docker'}
        self.level = 2
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False

        self.default_value = "None"
        self.value = self.default_value
        self.mark = False


class Format(BaseCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Docker = pre_obj
        self.root: Docker = root_obj
        self.next: Union[Format] = self
        self.meta_data = {'mapping_name': 'format', 'original_cmd': '--format', 'value': True, 'mutex': False,
                          'default': 'None', 'has_child_cmd': False, 'child_cmds': [], 'parent_cmd': 'Docker',
                          'root_cmd': 'Docker'}
        self.level = 2
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False

        self.default_value = "None"
        self.value = self.default_value
        self.mark = False


class Docker(Runner):
    def __init__(self, host=None, name=None, pwd=None, port="22", timeout="60", sudo=False):
        super().__init__()
        self.cmds: Cmds = Cmds()
        self.pre: object = None
        self.root: Docker = self
        self.next: Union[Ps, Inspect, Format,] = None
        self.main_cmd = "docker"
        self._mutexs = []
        self._gcs = []
        self._not_mutexs = []
        self.mode = "SSH"
        self.ssh_client = SSHClient(host, name, pwd, port)
        self._ps: Ps = Ps(self, self)
        self._inspect: Inspect = Inspect(self, self)
        self._format: Format = Format(self, self)

    def _set_ps(self):
        self._ps.mark = True
        self._ps.index = self.cmds.index
        self.cmds.index += 1
        self.next = self._ps
        self.cmds.CMD_LIST.append(self._ps)
        self._ps.cmds = self.cmds
        self._ps.ssh_client = self.ssh_client

    def tset_ps(self):
        """
        传递TRANSMIT模式，可以获取子命令对象，可通过，root/pre/next，控制命令对象的根/父/子级
        """
        self._set_ps()
        return self._ps

    def hset_ps(self, ):
        """
        保持HOLD模式，该方法返回该对象本身，不返回子对象
        """
        self._set_ps()
        return self

    def _set_inspect(self, value=None):
        self._inspect.mark = True
        self._inspect.index = self.cmds.index
        self.cmds.index += 1
        self.next = self._inspect
        self.cmds.CMD_LIST.append(self._inspect)
        self._inspect.cmds = self.cmds
        self._inspect.ssh_client = self.ssh_client

        if self._inspect.need_value:
            self._inspect.value = value

    def tset_inspect(self, value=None):
        """
        传递TRANSMIT模式，可以获取子命令对象，可通过，root/pre/next，控制命令对象的根/父/子级
        """
        self._set_inspect(value=value)
        return self._inspect

    def hset_inspect(self, value=None):
        """
        保持HOLD模式，该方法返回该对象本身，不返回子对象
        """
        self._set_inspect(value=value)
        return self

    def _set_format(self, value=None):
        self._format.mark = True
        self._format.index = self.cmds.index
        self.cmds.index += 1
        self.next = self._format
        self.cmds.CMD_LIST.append(self._format)
        self._format.cmds = self.cmds
        self._format.ssh_client = self.ssh_client

        if self._format.need_value:
            self._format.value = value

    def tset_format(self, value=None):
        """
        传递TRANSMIT模式，可以获取子命令对象，可通过，root/pre/next，控制命令对象的根/父/子级
        """
        self._set_format(value=value)
        return self._format

    def hset_format(self, value=None):
        """
        保持HOLD模式，该方法返回该对象本身，不返回子对象
        """
        self._set_format(value=value)
        return self

    def ps(self) -> Ps:
        return self._ps

    def inspect(self) -> Inspect:
        return self._inspect

    def format(self) -> Format:
        return self._format



