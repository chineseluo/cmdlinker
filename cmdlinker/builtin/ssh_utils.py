# -*- coding: utf-8 -*-
import os
import paramiko
import tempfile
import datetime
import sys
from cmdlinker.builtin import shell_utils
from loguru import logger
from cmdlinker.const import HostInfo


# default_print_fun = shell_utils.default_print_fun
def default_print_fun(x):
    print(x, file=sys.stderr)


def info_log(host, cmd, status_code, stdout, stderr):
    def _out_info(message):
        return f"""
execute cmd on host:{host}
execute cmd:{cmd}
status_code:{status_code}
response:\n{message}
        """

    if status_code == 0:
        logger.info(_out_info(stdout))
    else:
        logger.error(_out_info(stderr))


class SSHClient(object):
    def __init__(self, host, name=HostInfo.USER_NAME_BY_ROOT, password=HostInfo.PASSWORD, port=22, encoding='utf8'):
        self.host = host
        self.params = {'hostname': host, 'port': port}
        if name:
            self.params['username'] = name
        if password:
            self.params['password'] = password
        self.encoding = encoding
        self.client = paramiko.SSHClient()
        self.is_connected = False

    def __repr__(self):
        return f'SSHClient(host={self.host})'

    def check_connect(self):
        '''主要保证构造函数不要抛异常'''
        if self.is_connected:
            return
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(**self.params)
        self.is_connected = True

    def run_cmd(self, cmd, timeout=1800):
        self.check_connect()
        stdin_fd, stdout_fd, stderr_fd = self.client.exec_command(cmd, timeout=timeout)
        # 会阻塞
        status_code = stdout_fd.channel.recv_exit_status()  # status is 0
        stdout, stderr = stdout_fd.read().decode(self.encoding), stderr_fd.read().decode(self.encoding)
        info_log(self.host, cmd, status_code, stdout, stderr)
        return {'status_code': status_code, 'stdout': stdout, 'stderr': stderr}

    def run_cmd_output_console(self, cmd, print_fun=default_print_fun, timeout=36000):
        import datetime
        start_time = datetime.datetime.now()
        self.check_connect()
        stdin_fd, stdout_fd, stderr_fd = self.client.exec_command(cmd, timeout=timeout, bufsize=1)
        print_fun("cmd on %s:\ncmd: %s\n\n============\n\n" % (self.host, cmd))
        for out in iter(stdout_fd.readline, ''):
            if out: print_fun("%s" % (out))
        for err in iter(stderr_fd.readline, ''):
            if err: print_fun("%s" % (err))
        ret = stdout_fd.channel.recv_exit_status()  # status is 0
        end_time = datetime.datetime.now()
        during_time = end_time - start_time
        return {'ret': ret, "start_time": start_time, "end_time": end_time, "during_time": during_time.seconds}

    def exec(self, cmd):
        logger.info('cmd:' + cmd)
        self.check_connect()
        stdin, stdout, stderr = self.client.exec_command(cmd)
        for line in stdout:
            logger.info(line)
        logger.info(stderr.read())

    def run_cmd_by_subprocess(self, cmd):
        import subprocess
        online_upgrade_init_cmd = 'sshpass -p {} ssh -o "StrictHostKeyChecking no" {}@'.format(
            self.params['password'], self.params['username']) + self.host + ' "' + cmd + '" '
        retcode = subprocess.check_call(online_upgrade_init_cmd, shell=True, stderr=subprocess.STDOUT)
        return {'ret': retcode}

    def start_cmd(self, cmd, print_fun=default_print_fun):
        '''异步的 启动进程后返回 返回类型为SSHProcess'''
        self.check_connect()
        return SSHProcess(self.client, cmd, print_fun, self.encoding)

    def __copy_mod_from_local(self, local_file, remote_file, print_fun=default_print_fun):
        mod = shell_utils.check_output("stat -c%%a '%s'" % local_file, print_fun).strip()
        self.check_call("chmod %s '%s'" % (mod, remote_file), print_fun)

    def copy_from_local(self, local_file, remote_file, print_fun=default_print_fun, timeout=600):
        """
        从本地拷贝文件
        :param local_file:
        :param remote_file:
        :param print_fun:
        :param timeout:
        :return:
        """
        logger.info(
            "将本地的文件拷贝到远程服务器上，本地文件路径为：{}，远程服务器文件路径为：{}".format(local_file, remote_file))
        self.check_connect()
        # 1. 拷贝文件
        sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())
        sftp.get_channel().settimeout(timeout)
        sftp.put(local_file, remote_file)
        sftp.close()
        # 2. 拷贝权限
        # self.__copy_mod_from_local(local_file, remote_file, print_fun)

    def copy_dir_from_local(self, local_dir, remote_dir, tmp_dir='/tmp', print_fun=default_print_fun, timeout=600):
        '''先压缩 再拷贝...'''
        self.check_connect()
        timestamp = datetime.datetime.now().strftime('scp_%Y%m%d')
        # 1. 建立一个临时目录 主要是为了保证目录冲突
        tar_dir = tempfile.TemporaryDirectory(prefix=timestamp, dir=tmp_dir)
        self.check_call('mkdir -p %s' % tar_dir.name, print_fun, timeout)
        if self.call('test -d %s' % remote_dir, print_fun) == 0:
            raise Exception('already has %s on %s' % (remote_dir, self.host))
        self.check_call('mkdir -p %s' % remote_dir, print_fun)
        # 2. 打包
        tar_file = os.path.join(tar_dir.name, 'data.tgz')
        shell_utils.check_call('cd %s && tar czf %s *' % (local_dir, tar_file), print_fun, timeout)
        # 3. 拷贝
        sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())
        sftp.get_channel().settimeout(timeout)
        sftp.put(tar_file, tar_file)
        sftp.close()
        # 4. 解压
        self.check_call('tar xzf %s -C %s' % (tar_file, remote_dir), print_fun)

    def __copy_mod_from_remote(self, remote_file, local_file, print_fun=default_print_fun):
        mod = self.check_output("stat -c%%a '%s'" % remote_file, print_fun).strip()
        shell_utils.check_call("chmod %s '%s'" % (mod, local_file), print_fun)

    def copy_from_remote(self, remote_file, local_file, print_fun=default_print_fun, timeout=600):
        """
        从远程拷贝文件
        :param remote_file:
        :param local_file:
        :param print_fun:
        :param timeout:
        :return:
        """
        logger.info(
            "将远程服务器的文件拷贝到本地，远程服务器文件路径为：{}，文件路径为：{}".format(remote_file, local_file))
        self.check_connect()
        # 1. 拷贝文件
        sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())
        sftp.get_channel().settimeout(timeout)
        sftp.get(remote_file, local_file)
        sftp.close()
        # 2. 拷贝权限
        # self.__copy_mod_from_remote(remote_file, local_file, print_fun)

    def copy_dir_from_remote(self, local_dir, remote_dir, tmp_dir='/tmp', print_fun=default_print_fun, timeout=600):
        '''先压缩 再拷贝...'''
        self.check_connect()
        timestamp = datetime.datetime.now().strftime('scp_%Y%m%d')
        if shell_utils.call('test -d %s' % local_dir, print_fun) == 0:
            raise Exception('already has %s on local' % local_dir)
        shell_utils.check_call('mkdir -p %s' % local_dir, print_fun)
        # 1. 建立一个临时目录 主要是为了保证目录冲突
        tar_dir = tempfile.TemporaryDirectory(prefix=timestamp, dir=tmp_dir)
        self.check_call('mkdir -p %s' % tar_dir.name, print_fun, timeout)
        # 2. 打包
        tar_file = os.path.join(tar_dir.name, 'data.tgz')
        self.check_call('cd %s && tar czf %s *' % (local_dir, tar_file), print_fun, timeout)
        # 3. 拷贝
        sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())
        sftp.get_channel().settimeout(timeout)
        sftp.get(tar_file, tar_file)
        sftp.close()
        # 4. 解压
        shell_utils.check_call('tar xzf %s -C %s' % (tar_file, local_dir), print_fun)

    def assert_ret(self, ret, cmd, action):
        if ret != 0:
            if action:
                raise Exception('failed to %s on %s! ret=%d' % (action, self.host, ret))
            else:
                raise Exception('failed to run[%s] on %s! ret=%d' % (cmd, self.host, ret))

    def assert_ret_output_custom_info(self, ret, action):
        if ret != 0:
            if action:
                raise Exception("IP:{} 状态码:{} {}".format(self.host, ret, action))
            else:
                raise Exception("IP:{} 状态码:{} 执行jar包过程产生异常请处理！！！".format(self.host, ret))

    def check_output(self, cmd, print_fun=default_print_fun, timeout=600, action=None):
        result = self.run_cmd(cmd, print_fun, timeout)
        self.assert_ret(result['ret'], cmd, action)
        return result['stdout']

    def call(self, cmd, print_fun=default_print_fun, timeout=600):
        return self.run_cmd(cmd, print_fun, timeout)['ret']

    def check_call(self, cmd, print_fun=default_print_fun, timeout=600, action=None):
        result = self.run_cmd(cmd, print_fun, timeout)
        self.assert_ret(result['ret'], cmd, action)

    def check_call_output_console(self, cmd, print_fun=default_print_fun, timeout=3600, action=None):
        result = self.run_cmd_output_console(cmd, print_fun, timeout)
        logger.info("命令执行返回状态码：{}".format(result['ret']))
        self.assert_ret(result['ret'], cmd, action)

    def close(self):
        self.client.close()

    @classmethod
    def ssh_client_map_close(cls, ssh_client_map):
        """
        关闭map中的ssh_client, [原封不动复制于stepworker.agent_common]

        :param ssh_client_map:
        :return: 无
        """

        if ssh_client_map is None:
            return
        for client in ssh_client_map.values():
            if client is not None:
                client.close()


class SSHProcess:
    def __init__(self, client, cmd, print_fun, encoding):
        '''调用后返回'''
        self.client = client
        self.print_fun = print_fun
        self.cmd = cmd
        self.encoding = encoding
        self.stdin_fd, self.stdout_fd, self.stderr_fd = self.client.exec_command(cmd)

    def isRunning(self):  # NOSONAR
        '''返回是否运行中'''
        return not self.stdout_fd.channel.exit_status_ready()

    def done(self):
        '''返回retcode, stdout, stderr'''
        ret = self.stdout_fd.channel.recv_exit_status()  # status is 0
        stdout = self.stdout_fd.read().decode(self.encoding)
        stderr = self.stderr_fd.read().decode(self.encoding)
        return ret, stdout, stderr


if __name__ == '__main__':
    client = SSHClient('10.120.32.239', name='root', password='3keFWuBVyq')
