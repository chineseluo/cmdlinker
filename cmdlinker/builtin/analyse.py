from cmdlinker.builtin.yamlOption import FileOption
from loguru import logger
import json
from cmdlinker.model.models import Entry
from jinja2 import Template

yaml_data = FileOption.read_yaml("E:\开源项目\CmdLinker\Ost.yaml")
logger.info(json.dumps(yaml_data, indent=4))

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

# yaml文件检查
logger.info("**" * 20 + f"yaml文件合法性检查" + "**" * 20)
entry = Entry.parse_raw(json.dumps(yaml_data))
logger.debug(entry)
logger.info("**" * 20 + f"yaml合法性检查通过" + "**" * 20)

logger.info("==" * 20 + f"生成jinjia2模板渲染对象" + "==" * 20)

# yaml对象生成
sub_params_meta = []


def analyse_entry(meta_data):
    child_cmds = [parameter["mapping_name"] for parameter in meta_data["parameters"]]
    entry_meta = {
        "entry": meta_data["entry"],
        "mapping_entry": meta_data["mapping_entry"],
        "module_name": meta_data["module_name"],
        "class_name": meta_data["class_name"],
        "out_path": meta_data["out_path"],
        "has_child_cmd": False if len(child_cmds) == 0 else True,
        "child_cmds": child_cmds
    }
    return entry_meta


entry_meta = analyse_entry(yaml_data)
logger.debug(f"解析yaml主命令对象成功：{entry_meta}")


def analyse_var(params):
    for parameter in params:
        if "parameters" in parameter:
            analyse_var(parameter["parameters"])
            parameter.update({"has_child_cmd": True})
            parameter.update({"child_cmds": [parameter["mapping_name"] for parameter in parameter["parameters"]]})
            del parameter["parameters"]
            sub_params_meta.append(parameter)
        else:
            parameter.update({"has_child_cmd": False})
            parameter.update({"child_cmds": []})
            sub_params_meta.append(parameter)


analyse_var(yaml_data["parameters"])

[logger.debug(f"解析yaml子命令对象成功：{parameter}") for parameter in sub_params_meta]
logger.info("==" * 20 + f"jinjia2模板渲染对象生成成功" + "==" * 20)

# 生成命令对象
logger.info("==" * 20 + f"开始生成命令对象" + "==" * 20)

params_meta = {
    "entry_params_meta": entry_meta,
    "sub_params_meta": sub_params_meta
}
with open('E:\开源项目\CmdLinker\cmdlinker\\builtin\module_template.py.j2', 'r', encoding='utf-8') as f:
    template = f.read()
jinja_template = Template(template)
python_code = jinja_template.render(data=params_meta)
module_name = f'config_module.py'
with open(module_name, 'w', encoding="utf-8") as f:
    f.write(python_code)

exec(compile(source=open(module_name, encoding="utf-8").read(), filename=module_name, mode='exec'))
logger.info("==" * 20 + f"生成命令对象成功" + "==" * 20)
