# -*- coding: utf-8 -*-
"""
File Name：     shell_utils
Description :   大自然的搬运工 来源云平台工程
Author :        chenjingli
date：          2020/9/17
-------------------------------------------------
"""
import sys
import subprocess
from loguru import logger
# 默认打印到stderr
from cmdlinker.const import HostInfo


def default_print_fun(x):
    print(x, file=sys.stderr)


# 不打印
def none_print_fun(x):
    pass


def run_cmd(cmd, print_fun=default_print_fun, timeout=600):
    """
    执行命令 返回{'ret': <ret>, 'stdout': <stdout>, 'stderr': <stderr}
    """
    print_fun('running cmd: [%s]' % cmd)
    p = subprocess.Popen(
        cmd,
        shell=True,
        universal_newlines=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)
    try:
        (stdout, stderr) = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        print_fun('timeout!')
        p.kill()
        (stdout, stderr) = p.communicate()
    ret = p.returncode

    print_fun("======")
    print_fun("cmd:\n%s\n\nret:%d\n\nstdout:\n%s\n\nstderr:\n%s\n\n" % (cmd, ret, stdout, stderr))

    return {'ret': ret, 'stdout': stdout, 'stderr': stderr}


def __assert_ret(ret, cmd, action):
    if ret != 0:
        if action:
            raise Exception('failed to %s! ret=%d' % (action, ret))
        else:
            raise Exception('failed to run[%s]! ret=%d' % (cmd, ret))


def check_output(cmd, print_fun=default_print_fun, timeout=600, action=None):
    """
    执行命令 返回output 如果ret非0抛异常
    """
    result = run_cmd(cmd, print_fun, timeout)
    __assert_ret(result['ret'], cmd, action)
    return result['stdout']


def call(cmd, print_fun=default_print_fun, timeout=600):
    """
    执行命令 返回返回码
    """
    return run_cmd(cmd, print_fun, timeout)['ret']


def check_call(cmd, print_fun=default_print_fun, timeout=600, action=None):
    """
    执行命令，检查是否成功，不成功抛异常
    """
    result = run_cmd(cmd, print_fun, timeout)
    __assert_ret(result['ret'], cmd, action)


def run_cmd_by_sshpass(
        cmd_list=None,
        user_name=None,
        password=None,
        host=None,
        action=None,
        print_fun=default_print_fun):
    import subprocess
    cmd = ";".join(cmd_list)
    online_upgrade_init_cmd = 'sshpass -p {} ssh -o "StrictHostKeyChecking no" {}@'.format(
        password, user_name) + host + ' "' + cmd + '" '
    retcode = subprocess.check_call(online_upgrade_init_cmd, shell=True, stderr=subprocess.STDOUT)
    __assert_ret(retcode, cmd, action)


class ShellClient:
    '''跟SSHClient接口一样 用于本机的操作'''

    @staticmethod
    def run_cmd(cmd, print_fun=default_print_fun, timeout=600, encoding='utf-8'):
        return run_cmd(cmd, print_fun, timeout)

    @staticmethod
    # 通过免密的方式执行shell 命令为了Jenkins前段显示
    def run_cmd_by_sshpass(cmd_list=list(), user_name=HostInfo.USER_NAME_BY_ROOT,
                           password=HostInfo.PASSWORD, host='', print_fun=default_print_fun, action=None):
        return run_cmd_by_sshpass(cmd_list, user_name, password, host, print_fun, action)

    @staticmethod
    def start_cmd(cmd, print_fun=default_print_fun, encoding='utf-8'):
        return LocalProcess(cmd, print_fun, encoding)

    @staticmethod
    def copy_from_local(local_file, remote_file, print_fun=default_print_fun, timeout=600):
        check_call("cp --preserve=all '%s' '%s'" % (local_file, remote_file), print_fun, timeout)

    @staticmethod
    def copy_dir_from_local(local_dir, remote_dir, tmp_dir='/tmp', print_fun=default_print_fun, timeout=600):
        check_call("cp -r --preserve=all '%s' '%s'" % (local_dir, remote_dir), print_fun, timeout)

    @staticmethod
    def copy_from_remote(remote_file, local_file, print_fun=default_print_fun, timeout=600):
        check_call("cp --preserve=all '%s' '%s'" % (remote_file, local_file), print_fun, timeout)

    @staticmethod
    def copy_dir_from_remote(local_dir, remote_dir, tmp_dir='/tmp', print_fun=default_print_fun, timeout=600):
        check_call("cp -r --preserve=all '%s' '%s'" % (remote_dir, local_dir), print_fun, timeout)

    @staticmethod
    def check_output(cmd, print_fun=default_print_fun, timeout=600, action=None):
        return check_output(cmd, print_fun, timeout, action)

    @staticmethod
    def call(cmd, print_fun=default_print_fun, timeout=600):
        return call(cmd, print_fun, timeout)

    @staticmethod
    def check_call(cmd, print_fun=default_print_fun, timeout=600, action=None):
        return check_call(cmd, print_fun, timeout, action)

    def close(self):
        pass


class LocalProcess:
    def __init__(self, cmd, print_fun, encoding):
        self.cmd = cmd
        self.print_fun = print_fun
        self.p = subprocess.Popen(
            cmd,
            shell=True,
            universal_newlines=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)

    def isRunning(self):  # NOSONAR
        '''返回是否运行中'''
        return self.p.poll() is None

    def done(self):
        '''返回retcode, stdout, stderr'''
        ret = self.p.returncode
        stdout = self.p.stdout.read()
        stderr = self.p.stderr.read()
        return ret, stdout, stderr


if __name__ == '__main__':
    ShellClient.run_cmd_by_no_password(cmd_list=['cd /tmp', 'spadmin upgrader version'], password='pbwNPOlkWj',
                                       host='10.120.40.51')
