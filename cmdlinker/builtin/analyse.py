import os.path
import json
import time
from typing import Text
from cmdlinker.builtin.file_operation import FileOption
from loguru import logger
from cmdlinker.model.models import Entry
from jinja2 import Template

"""
入口检查
1、entry为主入口，不能为空
2、mapping_entry可以为空，使用entry，自动去除所有特殊字符，生成mapping_name
3、module_name同mapping_entry
4、class_name同mapping_entry
5、out_path默认当前目录
"""
# yaml合法性检查，赋予默认值
"""
1、 mapping_name可以为空，使用original_cmd，自动去除所有特殊字符，生成mapping_name
2、 value默认为True
3、 mutex默认为True
4、 default默认为None
"""


def check_yaml(file_path: Text):
    yaml_data = FileOption.read_yaml(file_path)
    # logger.info(json.dumps(yaml_data, indent=4))
    # yaml文件检查
    logger.info("**" * 20 + f"yaml文件合法性检查" + "**" * 20)
    entry = Entry.parse_raw(json.dumps(yaml_data))
    logger.debug(entry)
    logger.info("**" * 20 + f"yaml合法性检查通过" + "**" * 20)
    return yaml_data


# yaml对象生成
sub_params_meta = []


def analyse_entry(meta_data):
    child_cmds = [{"name": parameter["mapping_name"], "value": parameter["value"]} for
                                             parameter in meta_data["parameters"]]
    entry_meta = {
        "entry": meta_data["entry"],
        "mapping_entry": meta_data["mapping_entry"],
        "module_name": meta_data["module_name"],
        "class_name": meta_data["class_name"],
        "out_path": meta_data["out_path"],
        "has_child_cmd": False if len(child_cmds) == 0 else True,
        "child_cmds": child_cmds,
        "mode": meta_data["mode"].upper()
    }

    if meta_data["mode"].upper() == "SSH":
        ssh_conf = meta_data.get("ssh_conf", None)
        entry_meta.update({"ssh_conf": {
            "host": ssh_conf["ssh_host"] if ssh_conf else None,
            "name": ssh_conf["ssh_name"] if ssh_conf else None,
            "pwd": ssh_conf["ssh_pwd"] if ssh_conf else "22",
            "port": ssh_conf["ssh_port"] if ssh_conf else None,
            "sudo": ssh_conf["sudo"] if ssh_conf else False
        }})
    return entry_meta


def analyse_var(params, parent_cmd, root_cmd):
    for parameter in params:
        if "parameters" in parameter:
            parameter.update({"has_child_cmd": True})
            parameter.update({"parent_cmd": parent_cmd})
            parameter.update({"root_cmd": root_cmd})
            parameter.update({"child_cmds": [{"name": parameter["mapping_name"], "value": parameter["value"]} for
                                             parameter in parameter["parameters"]]})
            analyse_var(parameter["parameters"], parameter["mapping_name"], root_cmd)
            del parameter["parameters"]
            sub_params_meta.append(parameter)
        else:
            parameter.update({"has_child_cmd": False})
            parameter.update({"child_cmds": []})
            parameter.update({"parent_cmd": parent_cmd})
            parameter.update({"root_cmd": root_cmd})
            sub_params_meta.append(parameter)


def main(file_path: Text, out_path: Text, module_name: Text, class_name: Text):
    yaml_data = check_yaml(file_path)
    logger.info("==" * 20 + f"生成jinjia2模板渲染对象" + "==" * 20)
    entry_meta = analyse_entry(yaml_data)
    logger.debug(f"解析yaml主命令对象成功：{entry_meta}")
    analyse_var(yaml_data["parameters"], entry_meta["mapping_entry"], entry_meta["mapping_entry"])
    [logger.debug(f"解析yaml子命令对象成功：{parameter}") for parameter in sub_params_meta]
    logger.info("==" * 20 + f"jinjia2模板渲染对象生成成功" + "==" * 20)

    # 生成命令对象
    logger.info("==" * 20 + f"开始生成命令对象" + "==" * 20)
    params_meta = {
        "entry_params_meta": entry_meta,
        "sub_params_meta": sub_params_meta
    }
    base_path = os.path.abspath(os.path.dirname(__file__))
    jinja2_template = os.path.join(base_path, "module_template.py.j2")
    with open(jinja2_template, 'r', encoding='utf-8') as f:
        template = f.read()
    jinja_template = Template(template)
    python_code = jinja_template.render(data=params_meta)

    module_name = f'{entry_meta["module_name"] if module_name is None else module_name}.py'

    entry_meta["class_name"] = class_name if class_name is None else class_name
    out_module_path = os.path.join(out_path, module_name)
    with open(out_module_path, 'w', encoding="utf-8") as f:
        f.write(python_code)
    logger.info("==" * 20 + f"生成命令对象成功" + "==" * 20)


if __name__ == '__main__':
    main("E:\开源项目\CmdLinker\Ost.yaml", "./", None, None)
