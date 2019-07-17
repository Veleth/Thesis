import socket, threading
from user import User

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8000        # Port to listen on (non-privileged ports are > 1023)

rooms = {}
clients = []

def handle(data, conn):
    print(repr(data))

def sender(conn,addr):
    with conn:
        while True:
            conn.sendall(input().encode())

def on_new_connection(conn, addr):
    global rooms
    global clients
    user = User(conn, addr)
    with conn:
        print('Connected by', addr)
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                handle(data, conn)
        except ConnectionResetError:
            print('ConnectionResetError: ', addr, 'forcibly disconnected')
        finally:
            #TODO: remove the client
            print("Finally") 
            exit()

if (__name__== "__main__"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=on_new_connection, args=(conn, addr)).start()
                threading.Thread(target=sender, args=(conn, addr)).start()
            except KeyboardInterrupt:
                print("Over")
                exit()