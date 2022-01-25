import socket as _socket
from threading import RLock
from socket import *


class RLockSocket(object):
    def __init__(self, sock):
        self.__RLSsocket = sock
        self.__RLSlock = RLock()

    def __getattr__(self, attr):
        return getattr(self.__RLSsocket, attr)

    def accept(self, *a, **kw):
        with self.__RLSlock:
            conn, addr = self.__RLSsocket.accept(*a, **kw)
        return RLockSocket(conn), addr

    def sendall(self, *a, **kw):
        with self.__RLSlock:
            return self.__RLSsocket.sendall(*a, **kw)

    def send(self, *a, **kw):
        with self.__RLSlock:
            return self.__RLSsocket.send(*a, **kw)


def create_connection(*a, **kw):
    sock = _socket.create_connection(*a, **kw)
    return RLockSocket(sock)


def socket(*a, **kw):
    """ Replace socket.socket with an RLock protected socket via delegation"""
    sock = _socket.socket(*a, **kw)
    return RLockSocket(sock)
