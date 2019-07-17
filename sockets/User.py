import socket
class User():
    def __init__(self, conn, addr, is_GM = False):
        self.conn = conn
        self.addr = addr
        self.is_GM = is_GM
        # self.room = -1
        # self.name = ''
        # self.clientType = -1