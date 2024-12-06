from loguru import logger
from typing import Union


class Counter:
    index = 0


class CMDS:
    CMD_LIST = []


class OstCmd:
    def __init__(self):
        self.meta_data = None
        self.mutex = None
        self.need_value = None
        self.has_child_cmd = None
        self.gc = None
        self.child_cmds = None
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
            logger.error(f"命令对象：{self.__class__.__name__} 含有多个互斥对象，请检查：{self._mutexs}")
            raise Exception
        if len(self._mutexs) != 0 and len(self._not_mutexs) != 0:
            logger.error(f"命令对象：{self.__class__.__name__} 除全局命令外，不能同时存在互斥和非互斥命令，请检查：{self._mutexs},{self._not_mutexs}")
            logger.error("==" * 20 + f"命令{self.__class__.__name__}合法性检查不通过" + "==" * 20)
            raise Exception

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


class Port(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.meta_data = {
            "mapping_name": "port",
            "original_cmd": "-port"

        }
        self.level = 3
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = True
        self.gc = False
        self.child_cmds = False
        self.default_value = "8080"
        self.value = self.default_value
        self.mark = False
        self.index = 0
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Port] = self


class Run(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Run] = self
        self.meta_data = {
            "mapping_name": "run",
            "original_cmd": "-run"

        }
        self.level = 2
        self.mutex = False
        self.need_value = False
        self.has_child_cmd = True
        self.gc = False
        self._port: Port = Port(root_obj, self)
        self.default_value = "run cmd"
        self.value = self.default_value
        self.mark = False
        self._index = 0
        self.text = "wenben"

    def set_port(self, value=None):
        """

        1、检查是否被调用
        2、如果被调用，说明命令对象需要被解析
          1、检查是否需要值
          2、如果需要值，则看是否传递值，是否有默认值
        3、如果被未被调用，则需要被抛弃

        设置一个任务列表list
        当执行到对应的set命令，将cmdobj丢入任务列表，当需要进行子命令操作，则获取子命令对象操作，pre,next,root,
        :param value:
        :return:
        """
        self._port.mark = True
        self._port.index = Counter.index
        Counter.index += 1
        self.next = self._port
        self._port.ost_engine()
        CMDS.CMD_LIST.append(self._port)
        if self._port.need_value:
            self._port.value = value
            return self._port
        else:
            return self._port

    def port(self) -> Port:
        return self._port


class Start(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Run] = self
        self.meta_data = {
            "mapping_name": "start",
            "original_cmd": "-start"
        }
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = False
        self.gc = False
        self.child_cmds = []
        self.default_value = "start cmd"
        self.value = self.default_value
        self.mark = False
        self.index = 0
        self.level = 2


class GlobalCmd(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Run] = self
        self.meta_data = {
            "mapping_name": "globalcmd",
            "original_cmd": "-globalcmd"

        }
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = False
        self.gc = True
        self.child_cmds = []
        self.default_value = "global cmd"
        self.value = self.default_value
        self.mark = False
        self._index = 0
        self.level = 2


class Ost:

    def __init__(self):
        self._run: Run = Run(self, self)
        self._start: Start = Start(self, self)
        self._globalCmd: GlobalCmd = GlobalCmd(self, self)
        self.pre: object = None
        self.root: Ost = self
        self.next: Union[Start, Run] = None
        self.counter = Counter.index
        self.level = 1
        self._mutexs = []
        self._gcs = []
        self._not_mutexs = []
        self.main_cmd = "OST"
        # 需要检查子命令对象是否属于命令对象

    def set_run(self, value=None):
        """

        1、检查是否被调用
        2、如果被调用，说明命令对象需要被解析
          1、检查是否需要值
          2、如果需要值，则看是否传递值，是否有默认值
        3、如果被未被调用，则需要被抛弃

        设置一个任务列表list
        当执行到对应的set命令，将cmdobj丢入任务列表，当需要进行子命令操作，则获取子命令对象操作，pre,next,root,
        :param value:
        :return:
        """

        self._run.mark = True
        self._run.index = Counter.index
        Counter.index += 1
        self.next = self._run
        CMDS.CMD_LIST.append(self._run)

        self._run.ost_engine()
        if self._run.need_value:
            self._run.value = value
        return self._run

    def run(self) -> Run:
        return self._run

    def set_start(self, value=None) -> Start:
        """

        1、检查是否被调用
        2、如果被调用，说明命令对象需要被解析
          1、检查是否需要值
          2、如果需要值，则看是否传递值，是否有默认值
        3、如果被未被调用，则需要被抛弃

        :param value:
        :return:
        """
        self._start.mark = True
        self._start.index = Counter.index
        Counter.index += 1
        CMDS.CMD_LIST.append(self._start)
        self.next = self._start
        self._start.ost_engine()

        if self._start.need_value:
            self._start.value = value
        return self._start

    def start(self) -> Start:
        return self._start

    def set_globalCmd(self, value=None) -> GlobalCmd:
        """

        1、检查是否被调用
        2、如果被调用，说明命令对象需要被解析
          1、检查是否需要值
          2、如果需要值，则看是否传递值，是否有默认值
        3、如果被未被调用，则需要被抛弃

        :param value:
        :return:
        """
        self._globalCmd.mark = True
        self._globalCmd.index = Counter.index
        Counter.index += 1
        CMDS.CMD_LIST.append(self._globalCmd)
        self.next = self._globalCmd
        self._globalCmd.ost_engine()
        if self._globalCmd.need_value:
            self._globalCmd.value = value
        return self._globalCmd

    def globalCmd(self) -> GlobalCmd:
        return self._globalCmd

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
                    logger.debug(f"{self.main_cmd}添加互斥对象：{cmd_obj},最新互斥对象列表：{{self._mutexs}}")
                else:
                    self._not_mutexs.append(cmd_obj)
                    logger.debug(f"{self.main_cmd}添加非互斥对象：{cmd_obj},最新非互斥对象列表：{self._not_mutexs}")
        if len(self._mutexs) > 1:
            logger.error(f"含有多个互斥对象，请检查：{self._mutexs}")
            raise Exception
        if len(self._mutexs) != 0 and len(self._not_mutexs) != 0:
            logger.error(f"除全局命令，不能同时存在互斥和非互斥命令，请检查：{self._mutexs},{self._not_mutexs}")
            logger.error("==" * 20 + f"命令{self.__class__.__name__}合法性检查不通过" + "==" * 20)

            raise Exception
        # 全局命令可以和互斥命令同级
        # 全局命令可以和非互斥命令同级
        # 互斥命令之间不能同级 down
        # 互斥命令之间不能和非互斥命令同级 down
        # 非互斥命令之间可以同级别
        # 命令设置顺序，需要与set顺序一致，每个命令都会分配唯一索引，用于标记先后顺序
        # 1、合并命令列表，按照索引顺序排序
        logger.debug(f"解析命令列表前排序：{CMDS.CMD_LIST}")
        CMDS.CMD_LIST.sort(key=lambda cmd_obj: cmd_obj.index)
        logger.debug(f"解析命令列表后排序：{CMDS.CMD_LIST}")
        logger.info(f"执行命令列表：{[self.main_cmd] + [self._get_execute_cmd(cmd) for cmd in CMDS.CMD_LIST]}")


if __name__ == '__main__':
    ost = Ost()
    ost.set_run("test").set_port("9090").root.set_start("chineseluo").pre.set_globalCmd("global cmd test").ost_engine()
    # ost.set_run("test").set_port("9090").ost_engine()
    # engine命令检查，从下往前找，先找本对象是否存在问题，没有反递归向前找
    logger.info(ost.__dict__)
