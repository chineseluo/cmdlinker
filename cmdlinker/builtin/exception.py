from loguru import logger


class CmdLinkerException(Exception):
    """CmdLinker 基础异常"""
    ...


class CmdLinkerFileNotFountException(CmdLinkerException):
    ...


class CmdLinkerFileTypeException(CmdLinkerException):
    ...


class CmdLinkerCheckerException(CmdLinkerException):
    ...


class CmdLinkerApiException(CmdLinkerException):
    ...


class CmdLinkerArgvCheckException(CmdLinkerException):
    ...


class CmdLinkerMutexException(Exception):
    """CmdLinker 基础异常"""

    def __init__(self, obj_cmd, mutexs, not_mutexs):
        super().__init__(obj_cmd, mutexs, not_mutexs)
        logger.error(
            f"命令对象：{obj_cmd} 除全局命令外，不能同时存在互斥和非互斥命令，请检查：{mutexs},{not_mutexs}")
        logger.error("==" * 20 + f"命令{obj_cmd}合法性检查不通过" + "==" * 20)


class CmdLinkerMulMutexException(Exception):
    """CmdLinker 基础异常"""

    def __init__(self, obj_cmd, mutexs):
        super().__init__(obj_cmd, mutexs)
        logger.error(f"命令对象：{obj_cmd} 含有多个互斥对象，请检查：{mutexs}")
        logger.error("==" * 20 + f"命令{obj_cmd}合法性检查不通过" + "==" * 20)