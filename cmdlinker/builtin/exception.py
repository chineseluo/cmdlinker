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
    logger.exception(Exception)
