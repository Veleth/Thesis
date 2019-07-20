import socket, time, threading, hashlib, sys, names

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8000        # The port used by the server


def setState(state):
    print(state)

def send_info():
    s.sendall(input("> ").encode())

def handle_data(data):
    sys.stdout.write(str(data.decode()))
    if (len(data) > 5):
        print("Accepted")
    else:
        print("send me somethin")
        t1 = threading.Thread(target=send_info)
        t1.start()
        # t1.join()

def recv():
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    while True:
        data = s.recv(1024)
        if not data:
            break
        handle_data(data)
    print("An error has occured")

def init():
    #enter room and name
    input()    

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#SPECIFY host, port
s.connect((HOST, PORT))
threading.Thread(target=init).start().join()
threading.Thread(target=recv).start()

# print('Received', repr(data))