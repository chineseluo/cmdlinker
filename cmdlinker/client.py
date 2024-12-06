import sys
import argparse
from cmdlinker import __version__, __description__
from cmdlinker.builtin.cmd_conf import CmdLinkerCliConf
from cmdlinker.builtin.analyse import main
from loguru import logger
from termcolor import colored
import pyfiglet


def print_authors_info():
    figlet_text = pyfiglet.Figlet()
    color_text = figlet_text.renderText('CmdLinker')
    print(f"\n{colored(color_text, 'red')}")
    print(f"""The cmdlinker version is {__version__}
repository：https://github.com/chineseluo/cmdlinker
authors：成都-阿木木<848257135@qq.com>
community（QQ）：816489363""")


def init(*args, **kwarg):
    print_authors_info()

    main(args[0].file_path)
    # logger.info(*args)
    # logger.info(args[0].file_path)


def init_scaffold_parser(subparsers):
    testkeeper_cmd_conf = CmdLinkerCliConf().cmd_cli_conf
    sub_scaffold_parser_list = []
    for parent_cmd_info in testkeeper_cmd_conf["parameters"]:
        parent_cmd = parent_cmd_info['parent_cmd']
        sub_scaffold_parser = subparsers.add_parser(
            f"{parent_cmd['param_name']}", help=f"{parent_cmd['help']}",
        )
        sub_scaffold_parser.set_defaults(func=eval(parent_cmd['func']))
        if "children_cmd" in parent_cmd:
            for children_cmd_info in parent_cmd['children_cmd']:
                sub_scaffold_parser.add_argument(*children_cmd_info["param_name"],
                                                 type=eval(children_cmd_info["type"]), nargs="?",
                                                 help=children_cmd_info["help"],
                                                 default=children_cmd_info["default"],
                                                 dest=children_cmd_info["dest"])
            sub_scaffold_parser_list.append(sub_scaffold_parser)
    return sub_scaffold_parser_list


def print_child_help(sub_scaffold_parser_list, argv_list, argv_index):
    for sub_scaffold_parser in sub_scaffold_parser_list:
        if sub_scaffold_parser.prog.__contains__(argv_list[argv_index]):
            sub_scaffold_parser.print_help()


def entry():
    cl_argv = sys.argv
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-v", "-V", "--version", "--Version", help="show version", default=__version__)
    subparsers = parser.add_subparsers(help="TK cmd sub-command help")
    sub_scaffold_parser_list = init_scaffold_parser(subparsers)
    if len(cl_argv) == 1:
        parser.print_help()
        sys.exit()
    elif len(cl_argv) == 2:
        if cl_argv[1] in ["-V", "-v", "--Version", "--version"]:
            print_authors_info()
        elif cl_argv[1] in ["-h", "-H", "--help", "--Help"]:
            parser.print_help()
        else:
            args = parser.parse_args()
            try:
                args.func(args)
            except Exception as e:
                print_child_help(sub_scaffold_parser_list, cl_argv, 1)
                raise Exception(f"参数传递错误，异常信息{e}")
    elif len(cl_argv) == 3:
        if cl_argv[2] in ["-h", "-H", "--help", "--Help"]:
            print_child_help(sub_scaffold_parser_list, cl_argv, 1)
        else:
            print_child_help(sub_scaffold_parser_list, cl_argv, 1)
    else:
        logger.info(cl_argv)
        args = parser.parse_args()
        try:
            args.func(args)
        except Exception as e:
            print_child_help(sub_scaffold_parser_list, cl_argv, 1)
            raise Exception(f"参数传递错误，异常信息{e}")
    sys.exit(0)


if __name__ == '__main__':
    ...
