"""
User module

Implements User Class
"""

import socket
class User():
    """
    User class 

    Provides some abstraction for user object, used by the Server
    Attributes:
        conn       connection to the user
        addr       user address
        is_GM      whether user is a GM
        room       user room ID
        name       username
        value      user individual value
        result     user individual result
        trace      user individual trace
        secret     DH secret exchanged with the user
        key        encryption key
    """
    def __init__(self, conn, addr):
        """
        User constructor
        Input:
            conn    connection to the user
            addr    user address
        """
        self.conn = conn
        self.addr = addr
        self.is_GM = False
        self.room = None
        self.name = None
        self.value = None
        self.result = None
        self.trace = None
        self.secret = None
        self.key = None