import socket
class User():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.room = -1
        self.name = ''
        self.clientType = -1