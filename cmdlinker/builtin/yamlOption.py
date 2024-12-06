import yaml
import json
import os
from loguru import logger
from typing import Text, Dict, List
from cmdlinker.builtin.exception import CmdLinkerFileNotFountException
from cmdlinker.builtin.logger_operation import LoggerFormat


class FileOption:
    @staticmethod
    def read_yaml(file):
        """
        Read YML file
        :param file:
        :return:
        """
        if os.path.isfile(file):
            fr = open(file, 'r', encoding='utf-8')
            yaml_info = yaml.safe_load(fr)
            fr.close()
            # LoggerFormat.console_output("读取TestKeeper配置文件信息", yaml_info)
            return yaml_info
        else:
            raise CmdLinkerFileNotFountException(f'CmdLinker提示：【{file}】文件不存在!!!')

    @staticmethod
    def read_json(file):
        """
        Read YML file
        :param file:
        :return:
        """
        if os.path.isfile(file):
            fr = open(file, 'r', encoding='utf-8')
            json_info = json.loads(fr.read())
            fr.close()
            # LoggerFormat.console_output("读取TestKeeper配置文件信息", json_info)
            return json_info
        else:
            raise CmdLinkerFileNotFountException(f'TestKeeper提示：【{file}】文件不存在!!!')

    @staticmethod
    def create_dir(file_path: str):
        file_path = file_path.rstrip("\\")
        if os.path.exists(file_path):
            logger.info(f"文件目录{file_path}已存在，无需创建")
        else:
            logger.info(f"文件目录{file_path}不存在，开始创建目录")
            os.makedirs(file_path)