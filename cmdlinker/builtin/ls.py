from loguru import logger
from typing import Union
from cmdlinker.builtin.exception import CmdLinkerMutexException,CmdLinkerMulMutexException
from cmdlinker.builtin.ssh_utils import SSHClient
from cmdlinker.builtin.shell_utils import ShellClient


class Cmds:
    def __init__(self):
        self.index = 0
        self.CMD_LIST = []




class OstCmd:
    def __init__(self):
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
        self.main_cmd = "OST"
        self.pre: object = object
        self.root: object = object
        self.next: Union[object] = object

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

    def ost_engine(self, log_desc=""):
        start_log_desc = '' if self.next == self else self.next.__class__.__name__
        logger.info("=="*20+f"开启{start_log_desc} {log_desc}命令{self.__class__.__name__}合法性检查"+"=="*20)
        for cmd_obj_str in vars(self).keys():
            cmd_obj = getattr(self, cmd_obj_str)
            if isinstance(cmd_obj, OstCmd):
                if cmd_obj_str == "next":
                    continue
                if not self._exclude(cmd_obj):
                    continue
                if cmd_obj.mutex:
                    self._mutexs.append(cmd_obj)
                    logger.debug(f"命令对象：{self.__class__.__name__} 注入互斥对象：{cmd_obj},最新互斥列表对象列表为：{self._mutexs}")
                else:
                    self._not_mutexs.append(cmd_obj)
                    logger.debug(f"命令对象：{self.__class__.__name__} 注入非互斥对象：{cmd_obj}，最新非互斥列表对象列表为：{self._not_mutexs}")

        if len(self._mutexs) > 1:
            raise CmdLinkerMulMutexException(self.__class__.__name__, self._mutexs)
        if len(self._mutexs) != 0 and len(self._not_mutexs) != 0:
            raise CmdLinkerMutexException(self.__class__.__name__, self._mutexs, self._not_mutexs)

        if self.pre == self.root:
            logger.debug(f"启用命令对象{self.__class__.__name__} root 命令: {self.root.__class__.__name__} 检查")
            self.root.ost_engine(log_desc="root")
            self.root._not_mutexs = []
            self.root._mutexs = []
            logger.debug(f"清理命令对象{self.__class__.__name__} root 命令: {self.root.__class__.__name__}互斥与否检查数据")
        else:
            logger.debug(f"启用命令对象{self.__class__.__name__} pre 命令: {self.pre.__class__.__name__} 检查")

            self.pre.ost_engine(log_desc="pre")
            self.pre._not_mutexs = []
            self.pre._mutexs = []
            logger.debug(f"清理命令对象{self.__class__.__name__}父命令: {self.pre.__class__.__name__}互斥与否检查数据")
        logger.info("=="*20+f"命令{self.next.__class__.__name__} {log_desc}合法性检查通过"+"=="*20)



class L(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ls = pre_obj
        self.root: Ls = root_obj
        self.next: Union[L] = self
        self.meta_data = {'mapping_name': 'l', 'original_cmd': '-l', 'value': False, 'mutex': False, 'default': 'None', 'has_child_cmd': False, 'child_cmds': [], 'parent_cmd': 'Ls', 'root_cmd': 'Ls'}
        self.level = 2
        self.mutex = False
        self.need_value = False
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False
        
        self.default_value =  "None" 
        self.value = self.default_value
        self.mark = False
    




class Ls:

    def __init__(self  ,host= "47.97.37.176" ,name= "root" ,pwd= "luo@848257135" ,port= 22 ,sudo= False  ):
        self.cmds: Cmds = Cmds()
        self.pre: object = None
        self.root: Ls = self
        self.next: Union[L,] = None
        self.main_cmd = "ls"
        self._mutexs = []
        self._gcs = []
        self._not_mutexs = []
        self.mode = "SSH"
        
        self.ssh_client = SSHClient(host, name, pwd, port)
        
        
        self._l:L = L(self,self)
        
    
    def set_l(self):
        self._l.mark = True
        self._l.index = self.cmds.index
        self.cmds.index += 1
        self.next = self._l
        self.cmds.CMD_LIST.append(self._l)

        self._l.ost_engine()
        
        return self._l
    

    
    def l(self) -> L:
        return self._l
    

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

    def ost_engine(self, log_desc=""):
        for cmd_obj_str in vars(self).keys():
            cmd_obj = getattr(self, cmd_obj_str)
            if isinstance(cmd_obj, OstCmd):
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

        logger.debug(f"解析命令列表前排序：{self.cmds.CMD_LIST}")
        self.cmds.CMD_LIST.sort(key=lambda cmd_obj: cmd_obj.index)
        logger.debug(f"解析命令列表后排序：{self.cmds.CMD_LIST}")

    def runner(self):
        logger.info(f"执行命令列表：{[self.main_cmd] + [self._get_execute_cmd(cmd) for cmd in self.cmds.CMD_LIST]}")
        cmd_list = [self.main_cmd] + [self._get_execute_cmd(cmd) for cmd in self.cmds.CMD_LIST]
        cmd = " ".join(cmd_list)

        return self.ssh_client.run_cmd(cmd)
        



if __name__ == '__main__':
    ls = Ls().set_l().root.runner()