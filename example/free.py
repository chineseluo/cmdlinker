import time

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
        self.timeout: int = 60

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
        self.main_cmd = "free"
        self.pre: object = object
        self.root: object = object
        self.next: Union[object] = object
        self.ssh_client: SSHClient = None


class B(BaseCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Free = pre_obj
        self.root: Free = root_obj
        self.next: Union[B] = self
        self.meta_data = {'mapping_name': 'b', 'original_cmd': '-b', 'value': False, 'mutex': False, 'default': 'None',
                          'has_child_cmd': False, 'child_cmds': [], 'parent_cmd': 'Free', 'root_cmd': 'Free'}
        self.level = 2
        self.mutex = False
        self.need_value = False
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False

        self.default_value = "None"
        self.value = self.default_value
        self.mark = False


class T(BaseCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Free = pre_obj
        self.root: Free = root_obj
        self.next: Union[T] = self
        self.meta_data = {'mapping_name': 't', 'original_cmd': '-t', 'value': False, 'mutex': False, 'default': 'None',
                          'has_child_cmd': False, 'child_cmds': [], 'parent_cmd': 'Free', 'root_cmd': 'Free'}
        self.level = 2
        self.mutex = False
        self.need_value = False
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False

        self.default_value = "None"
        self.value = self.default_value
        self.mark = False


class Free(Runner):
    def __init__(self, host=None, name=None, pwd=None, port="22", timeout="60", sudo=False):
        super().__init__()
        self.cmds: Cmds = Cmds()
        self.pre: object = None
        self.root: Free = self
        self.next: Union[B, T,] = None
        self.main_cmd = "free"
        self._mutexs = []
        self._gcs = []
        self._not_mutexs = []
        self.mode = "SSH"
        self.ssh_client = SSHClient(host, name, pwd, port)
        self._b: B = B(self, self)
        self._t: T = T(self, self)

    def _set_b(self):
        self._b.mark = True
        self._b.index = self.cmds.index
        self.cmds.index += 1
        self.next = self._b
        self.cmds.CMD_LIST.append(self._b)
        self._b.cmds = self.cmds
        self._b.ssh_client = self.ssh_client

    def tset_b(self):
        """
        传递TRANSMIT模式，可以获取子命令对象，可通过，root/pre/next，控制命令对象的根/父/子级
        """
        self._set_b()
        return self._b

    def hset_b(self, ):
        """
        保持HOLD模式，该方法返回该对象本身，不返回子对象
        """
        self._set_b()
        return self

    def _set_t(self):
        self._t.mark = True
        self._t.index = self.cmds.index
        self.cmds.index += 1
        self.next = self._t
        self.cmds.CMD_LIST.append(self._t)
        self._t.cmds = self.cmds
        self._t.ssh_client = self.ssh_client

    def tset_t(self):
        """
        传递TRANSMIT模式，可以获取子命令对象，可通过，root/pre/next，控制命令对象的根/父/子级
        """
        self._set_t()
        return self._t

    def hset_t(self, ):
        """
        保持HOLD模式，该方法返回该对象本身，不返回子对象
        """
        self._set_t()
        return self

    def b(self) -> B:
        return self._b

    def t(self) -> T:
        return self._t


if __name__ == '__main__':
    free = Free(host="47.97.37.176", name="root", pwd="luo@848257135")
    free.hset_b().hset_t().runner()
    logger.info(int(time.time()*1000))
