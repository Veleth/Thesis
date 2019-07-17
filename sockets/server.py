import socket, threading, User

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8000        # Port to listen on (non-privileged ports are > 1023)

rooms = {}
clients = []


def on_new_connection(conn, addr):
    with conn:
        print('Connected by', addr)
        while True: #echo
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
            

if (__name__== "__main__"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=on_new_connection, args=(conn, addr)).start()
            except KeyboardInterrupt:
                print("Over")
                exit()

