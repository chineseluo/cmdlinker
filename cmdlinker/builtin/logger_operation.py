import json
import sys
from loguru import logger
from typing import List, Text, Dict, Union
from prettytable import PrettyTable
from prettytable import DEFAULT


class LoggerFormat:

    @staticmethod
    def console_output(title: Text, result: Dict):
        msg = f"\n================== {title}  details ==================\n"
        for key, value in result.items():
            if isinstance(value, (Dict, List)):
                value = json.dumps(value, indent=4, ensure_ascii=False)
            msg += "{:<8} : {}\n".format(key, value)
        logger.info(msg)

    @staticmethod
    def console_pretty_table(title: Text, content: Union[List, Dict]):
        pt = PrettyTable()
        pt.title = title
        filed_names = []
        content_list = []
        if isinstance(content, List):
            for item in content:
                if isinstance(item, Dict):
                    child_content_list = []
                    for i in item:
                        if len(filed_names) == len(item.items()):
                            pass
                        else:
                            filed_names.append(i)
                        child_content_list.append(item[i])
                    content_list.append(child_content_list)
            if len(content_list) == 0:
                pt.field_names = ["查询结果显示"]
                pt.add_row(["查询显示无数据"])
            else:
                pt.field_names = filed_names
                pt.add_rows(content_list)
        elif isinstance(content, Dict):
            for item in content:
                filed_names.append(item)
                content_list.append(content[item])
            pt.field_names = filed_names
            pt.add_row(content_list)
        pt.set_style(DEFAULT)
        logger.info(f"\n{pt}")
