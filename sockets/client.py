import socket, time, threading, hashlib

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8000        # The port used by the server


def setState(state):
    print(state)

def handle_data(data):
    print("Data: ", data)

def recv():
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    while True:
        data = s.recv(1024)
        if not data:
            break
        handle_data(data)
    print("An error has occured")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
threading.Thread(target=recv).start()
while True:
    s.sendall(input().encode())

# print('Received', repr(data))