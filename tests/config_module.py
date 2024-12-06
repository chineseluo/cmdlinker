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



class Desc(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Desc] = self
        self.meta_data = {'mapping_name': 'desc', 'original_cmd': '-desc', 'value': True, 'mutex': False, 'default': 'desc', 'has_child_cmd': False, 'child_cmds': []}
        self.level = 2
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False
        
        self.default_value =  "desc" 
        self.value = self.default_value
        self.mark = False
        self._index = 0
    




class Port(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Port] = self
        self.meta_data = {'mapping_name': 'port', 'original_cmd': '-port', 'value': True, 'mutex': False, 'default': '8080', 'has_child_cmd': True, 'child_cmds': ['desc']}
        self.level = 2
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = True
        self.child_cmds = ['desc']
        self.gc = False
        
        self._desc: Desc = Desc(root_obj, self)
        
        self.default_value =  "8080" 
        self.value = self.default_value
        self.mark = False
        self._index = 0
    
    def set_desc(self, value=None):
        self._desc.mark = True
        self._desc.index = Counter.index
        Counter.index += 1
        self.next = self._port
        self._desc.ost_engine()
        CMDS.CMD_LIST.append(self._port)
        if self._desc.need_value:
            self._desc.value = value
            return self._desc
        else:
            return self._desc

    def desc(self) -> Desc:
        return self._desc
    




class Host(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Host] = self
        self.meta_data = {'mapping_name': 'host', 'original_cmd': '-host', 'value': True, 'mutex': False, 'default': 'www.baidu.com', 'has_child_cmd': False, 'child_cmds': []}
        self.level = 2
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False
        
        self.default_value =  "www.baidu.com" 
        self.value = self.default_value
        self.mark = False
        self._index = 0
    




class Run(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Run] = self
        self.meta_data = {'mapping_name': 'run', 'original_cmd': '-run_it', 'value': True, 'mutex': False, 'default': 'None', 'has_child_cmd': True, 'child_cmds': ['port', 'host']}
        self.level = 2
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = True
        self.child_cmds = ['port', 'host']
        self.gc = False
        
        self._port: Port = Port(root_obj, self)
        
        self._host: Host = Host(root_obj, self)
        
        self.default_value =  "None" 
        self.value = self.default_value
        self.mark = False
        self._index = 0
    
    def set_port(self, value=None):
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
    
    def set_host(self, value=None):
        self._host.mark = True
        self._host.index = Counter.index
        Counter.index += 1
        self.next = self._port
        self._host.ost_engine()
        CMDS.CMD_LIST.append(self._port)
        if self._host.need_value:
            self._host.value = value
            return self._host
        else:
            return self._host

    def host(self) -> Host:
        return self._host
    




class Plan_Load(OstCmd):
    def __init__(self, root_obj, pre_obj):
        super().__init__()
        self.pre: Ost = pre_obj
        self.root: Ost = root_obj
        self.next: Union[Plan_Load] = self
        self.meta_data = {'mapping_name': 'plan_load', 'original_cmd': '-plan_load', 'value': True, 'mutex': False, 'default': None, 'has_child_cmd': False, 'child_cmds': []}
        self.level = 2
        self.mutex = False
        self.need_value = True
        self.has_child_cmd = False
        self.child_cmds = []
        self.gc = False
        
        self.default_value =  None 
        self.value = self.default_value
        self.mark = False
        self._index = 0
    




class Ost:

    def __init__(self):
        self.pre: object = None
        self.root: Ost = self
        self.next: Union[ Run, Plan_Load,] = None
        self.counter = Counter.index
        self.main_cmd = ""
        self._mutexs = []
        self._gcs = []
        self._not_mutexs = []
        
        self._run:Run = Run(self,self)
        
        self._plan_load:Plan_Load = Plan_Load(self,self)
        
    
    def set_run(self, value=None):
        self._run.mark = True
        self._run.index = Counter.index
        Counter.index += 1
        self.next = self._run
        CMDS.CMD_LIST.append(self._run)

        self._run.ost_engine()
        if self._run.need_value:
            self._run.value = value
        return self._run
    
    def set_plan_load(self, value=None):
        self._plan_load.mark = True
        self._plan_load.index = Counter.index
        Counter.index += 1
        self.next = self._run
        CMDS.CMD_LIST.append(self._plan_load)

        self._plan_load.ost_engine()
        if self._plan_load.need_value:
            self._plan_load.value = value
        return self._plan_load
    

    
    def run(self) -> Run:
        return self._run
    
    def plan_load(self) -> Plan_Load:
        return self._plan_load
    

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
            logger.error(f"含有多个互斥对象，请检查：{self._mutexs}")
            raise Exception
        if len(self._mutexs) != 0 and len(self._not_mutexs) != 0:
            logger.error(f"除全局命令，不能同时存在互斥和非互斥命令，请检查：{self._mutexs},{self._not_mutexs}")
            logger.error("==" * 20 + f"命令{self.__class__.__name__}合法性检查不通过" + "==" * 20)
            raise Exception
        logger.debug(f"解析命令列表前排序：{CMDS.CMD_LIST}")
        CMDS.CMD_LIST.sort(key=lambda cmd_obj: cmd_obj.index)
        logger.debug(f"解析命令列表后排序：{CMDS.CMD_LIST}")
        logger.info(f"执行命令列表：{[self.main_cmd] + [self._get_execute_cmd(cmd) for cmd in CMDS.CMD_LIST]}")