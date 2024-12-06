from pydantic import BaseModel, validator, Field
from typing import Text, Any, List, Optional
import re
from loguru import logger


def check_special_char(key, value):
    special_char_pattern = r'[^a-zA-Z0-9_ ]'
    pattern = re.compile(special_char_pattern)
    if pattern.search(value):
        raise ValueError(f"{key}:[{value}] 含有特殊字符，在强校验模式下不可用，请检查yaml文件的{key}字段")
    return value


class SubCmd(BaseModel):
    mapping_name: Text = None
    original_cmd: Text = None
    value: bool = True
    mutex: bool = False
    default: Any = None
    parameters:  Optional[List["SubCmd"]] = None

    @validator("mapping_name")
    def check_mapping_name(cls, value):
        return check_special_char("mapping_name", value)


class Entry(BaseModel):
    entry: Text = None
    mapping_entry: Text = None
    module_name: Text = None
    class_name: Text = None
    out_path: Text = "./"
    parameters: Optional[List[SubCmd]] = None

    @validator("entry")
    def check_entry(cls, value):
        return check_special_char("entry", value)

    @validator("mapping_entry")
    def check_mapping_entry(cls, value):
        return check_special_char("mapping_entry", value)

    @validator("module_name")
    def check_module_name(cls, value):
        return check_special_char("module_name", value)

    @validator("class_name")
    def check_class_name(cls, value):
        return check_special_char("class_name", value)
