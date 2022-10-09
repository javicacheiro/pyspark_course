import paramiko
import getpass
import subprocess


def run(cmd, host='local', user=None, key_filename='/opt/airflow/dags/keys/id_rsa'):
    """Runs the given command locally or in the remote host using SSH"""
    if host != 'local':
        if user is None:
            user = getpass.getuser()
        client = SSHClient(user, host, key_filename)
        stdout, stderr, returncode = client.run(cmd)
        if returncode != 0:
            raise RunCommandError(stderr)
        return stdout, stderr
    p = subprocess.run(cmd, shell=True, capture_output=True)
    if p.returncode != 0:
        raise RunCommandError(p.stderr)
    return p.stdout.decode('utf8'), p.stderr.decode('utf8')


class RunCommandError(Exception):
    pass


class SSHClient:
    """Remote client using SSH to run commands

        >>> client = SSHClient('cursoXXX', 'hadoop.cesga.es', key_filename='/opt/airflow/dags/keys/id_rsa')
        >>> client.run('/bin/hostname')

        :param user: remote ssh user
        :param host: remote ssh host
        :param cmd: command to execute remotely
        :param key_filename:
    """
    def __init__(self, user, host, key_filename='config/keys/id_rsa'):
        self.user = user
        self.host = host
        self.key_filename = key_filename

    def run(self, cmd, host=None):
        """Runs a command in a remote host using SSH and returns the result

        >>> client.run('/bin/hostname')
        (b'hadoop.cesga.es\n', b'')

        :param cmd: command to execute remotely
        :param host: host to connect, if different from default one
        :return: stdout and stderr output
        :rtype: bytes
        """
        if not host:
            host = self.host
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=self.user,
                       key_filename=self.key_filename,
                       timeout=5)
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        exit = stdout.channel.recv_exit_status()
        return stdout.read().decode('utf8'), stderr.read().decode('utf8'), exit
