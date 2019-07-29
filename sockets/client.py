import socket, time, threading, hashlib, sys
from communication import *

class Client:
    def __init__(self, HOST, PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        initializer = threading.Thread(target=self.init)
        initializer.start()
        # initializer.join()
        threading.Thread(target=self.recv).start()

    def send_info(self):
        self.sock.sendall(input("> ").encode())

    def handle_data(self, data):
        sys.stdout.write(str(data.decode()))
        # if (len(data) > 5):
        #     print("Accepted")
        # else:
        #     print("send me somethin")
        #     t1 = threading.Thread(target=send_info)
        #     t1.start()
        #     # t1.join()

    def recv(self):
        while True:
            data = self.sock.recv(128)
            if not data:
                break
            self.handle_data(data)
        print("An error has occured")

    def validated_input(self, message):
        ans = input(message)
        while not ans.isalnum():
            print("Wrong! Only alphanumeric non-empty strings allowed. Try again!")
            ans = input(message)
        return ans

    def init(self):
        room = 21 #self.validated_input("Enter the number of the room: ")
        username ="ABCDEF" #self.validated_input("Enter your username")    
        message = compose(INIT_HEADER, [room, username])
        self.sock.sendall(message)

client = Client('127.0.0.1', 8000)