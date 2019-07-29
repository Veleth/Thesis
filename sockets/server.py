import socket, threading, time, datetime, sys, hashlib, random
from user import User
from communication import *

class Server:
    def __init__(self, HOST, PORT, LOGFILE=sys.stdout):
        self.HOST = HOST     # Standard loopback interface address (localhost)
        self.PORT = PORT     # Port to listen on (non-privileged ports are > 1023)
        self.rooms = {}
        self.LOGFILE = LOGFILE
        self.dispatch = {
            INIT_HEADER : self.init,
            # ROLL_HEADER : self.roll,
            # CHAT_HEADER : self.chat,
            # RESULT_HEADER : self.result,
            # TRACE_HEADER : self.trace,
            # VAR_HEADER : self.var
        }
        self.run()
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=self.on_new_connection, args=(conn, addr)).start()
                    threading.Thread(target=self.sender, args=(conn, addr)).start()
                except KeyboardInterrupt:
                    print("Over")
                    exit()

    def send_room(self, room, message, players = None):
        for player in self.rooms[room]:
            if (players == None or player in players):
                player.conn.sendall(message)

    def handle(self, data, conn, user):
        messages = decompose(data)
        for message in messages:
            m = list(filter(None, message.split(MESSAGE_DELIMITER)))
            print(m)
            if m[0] in self.dispatch.keys():
                self.dispatch[m[0]](m, user)
            else:
                raise UndefinedHeaderException(m[0])

    def sender(self, conn, addr):
        with conn:
            while True:
                conn.sendall(input().encode())

    def on_new_connection(self, conn, addr):
        user = User(conn, addr)
        with conn: #TODO: Init player and add to room
            print(datetime.datetime.now(), ': Connected by', addr, file=self.LOGFILE)
            try:
                while True:
                    data = conn.recv(128)
                    if not data:
                       break
                    self.handle(data, conn, user)
            except ConnectionResetError:
                print('ConnectionResetError: ', addr, 'forcibly disconnected')
            finally:
                #TODO: remove the client
                print("Finally") 
                exit()

    def init(self, message, newUser):
        room = message[1]
        username = message[2]
        if room in self.rooms:
            newUser.room = room
            self.rooms[room].append(newUser)
            for user in self.rooms[room]:
                if user.name == username:
                    #name taken TODO: collision elimination
                    username = str(username+"_"+hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5])
            newUser.name = username
            msg = str(username+" has joined the room!")
            self.send_room(room, compose(INFO_HEADER,msg))
        else:
            self.rooms[room] = []
            newUser.room = room
            newUser.name = username
            newUser.isGM = True
            self.rooms[room].append(newUser)
            msg = [str("You have joined the room "+room+" as a GM+\n")]
            #TODO: msg+= "Use roll to roll"
            self.send_room(room, compose(INFO_HEADER,msg))

server = Server('127.0.0.1', 8000)
        # self.LOGFILE=sys.stdout #open('server.log', 'a')