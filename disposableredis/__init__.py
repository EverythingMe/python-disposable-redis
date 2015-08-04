import subprocess
import socket
import tempfile
import redis
import time
import os


def get_random_port():
    sock = socket.socket()
    sock.listen(0)
    _, port = sock.getsockname()
    sock.close()

    return port


class DisposableRedis(object):
    def __init__(self, port=None):
        """
        :param port: port number to start the redis server on. Specify none to automatically generate
        :type port: int|None
        """

        self._port = port

        # this will hold the actual port the redis is listening on. It's equal to `_port` unless `_port` is None
        # in that case `port` is randomly generated
        self.port = None

    def __enter__(self):
        if self._port is None:
            self.port = get_random_port()
        else:
            self.port = self._port

        self.process = subprocess.Popen(
            ['redis-server',
             '--port', str(self.port),
             '--dir', tempfile.gettempdir(),
             '--save', ''],
            stdin=subprocess.PIPE,
            stdout=open(os.devnull, 'w')
        )
        self.process.stdin.close()

        while True:
            try:
                self.client().ping()

                break
            except redis.ConnectionError:
                time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process.terminate()

    def client(self):
        """
        :rtype: redis.StrictRedis
        """

        return redis.StrictRedis(port=self.port)

