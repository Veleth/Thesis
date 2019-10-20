import socket, threading, time, datetime, sys, hashlib, random

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8000

def sendx(conn,addr):
    time.sleep(5)
    conn.sendall("test".encode())
    print("done")
    
def serve(conn, addr):
    counter = 1000
    with conn:
        print(datetime.datetime.now(), ': Connected by', addr)
        try:
            while True:
                data = conn.recv(10)
                print(data)
                if not data:
                    break
                # conn.sendall(str(counter).encode())
                # counter += 1
                # time.sleep(3)
        except ConnectionResetError:
            print('ConnectionResetError: ', addr, 'forcibly disconnected')
        finally:
            print("Finally") 
            exit()

if (__name__== "__main__"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                import pyDHE
                alice = pyDHE.new()
                key = alice.negotiate(conn)
                print(key)
                threading.Thread(target=serve, args=(conn, addr)).start()
                threading.Thread(target=sendx, args=(conn, addr)).start()
            except KeyboardInterrupt:
                print("Over")
                exit()