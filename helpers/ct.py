import socket, time, threading, hashlib, sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8000        # The port used by the server

def recv():
    while True:
        data = s.recv(10)
        print(data)
        if not data:
            break
    print("receiving issue")

def snd():
    iter = 1
    counter = -1000
    while True:
        s.sendall(str(counter).encode())
        print("sending")
        counter -= 1
        time.sleep(iter)
        iter += 1
    print("sending issue")

def keyExchange():
    pass


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#SPECIFY host, port
s.connect((HOST, PORT))
import pyDHE
print(s.getsockname())
# alice = pyDHE.new()
# key = alice.negotiate(s)
# print(key)

threading.Thread(target=recv).start()
threading.Thread(target=snd).start()

