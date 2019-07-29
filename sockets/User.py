import socket
class User():

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.is_GM = False
        self.room = None
        self.name = None