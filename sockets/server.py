import socket, threading, time, datetime, sys, hashlib, random
from user import User
from room import Room
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

    def sender(self): #TODO: For testing purposes; Remove afterwards
        while True:
            action = input()
            if action == "1":
                message = "CHAT|Player1|Catch me if u can\\"
            elif action == "2":
                message = "ROLL|Player2\\" #TODO: Ideas for improvement
            elif action == "3":
                message = "VAR|a8993|abc339\\"
            else:
                 message = action
            
            for room in self.rooms:
                for player in self.rooms[room].players:
                    player.conn.sendall(message.encode())

    def run(self):
        threading.Thread(target=self.sender).start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=self.on_new_connection, args=(conn, addr)).start()
                except KeyboardInterrupt:
                    print("Over")
                    exit()

    def send_room(self, room, message, players = None):
        for player in self.rooms[room].players:
            if (players == None or player in players):
                player.conn.sendall(message)
    
    def send_message(self, player, message):
        player.conn.sendall(message)

    def list_players(self, room):
        lst = []
        for player in self.rooms[room].players:
            if player.is_GM:
                lst.append(str(player.name+" (GM)"))
            elif player.name:
                lst.append(str(player.name))
        return ", ".join(lst)

    def handle(self, data, conn, user):
        messages = decompose(data)
        for message in messages:
            m = list(filter(None, message.split(MESSAGE_DELIMITER)))
            print(m)
            if m[0] in self.dispatch.keys():
                self.dispatch[m[0]](m, user)
            else:
                raise UndefinedHeaderException(m[0])

    def on_new_connection(self, conn, addr):
        user = User(conn, addr)
        with conn: #Start listening for messages
            print(datetime.datetime.now(), ': Connected by', addr, file=self.LOGFILE)
            try:
                while True:
                    data = conn.recv(128)
                    if not data:
                       break
                    self.handle(data, conn, user)
            except ConnectionResetError:
                print('ConnectionResetError: ', addr, 'forcibly disconnected', file=self.LOGFILE)
            finally:
                #Remove the client from their room
                if user.room is not None: #TODO: What if gm leaves?
                    self.rooms[user.room].players.remove(user)
                    #If the room has been emptied
                    if not self.rooms[user.room].players:
                        del self.rooms[user.room] #VOLATILE #or self.rooms.pop(user.room)

    def init(self, message, newUser):
        #INIT MESSAGE STRUCTURE ['INIT', '$room', '$username']
        room = message[1]
        username = message[2]
        if room in self.rooms:
            newUser.room = room
            self.rooms[room].players.append(newUser)
            for user in self.rooms[room].players: #TODO: refine
                if user.name == username and user is not newUser:
                    # name taken TODO: collision elimination
                    username = str(username+"_"+hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5])
            newUser.name = username
            msg = str(username+" has joined the room!")
            self.send_room(room, compose(INFO_HEADER,[msg]))
            msg = str("Players in this room: "+self.list_players(room))
            self.send_message(newUser, compose(INFO_HEADER,[msg]))
        else:
            self.rooms[room] = Room()
            newUser.room = room
            newUser.name = username
            newUser.is_GM = True
            self.rooms[room].players.append(newUser)
            msg = str("You have joined the room "+room+" as a GM\n")
            #TODO: msg+= "Use roll to roll"
            self.send_message(newUser, compose(INFO_HEADER,[msg]))

    # ROLL_HEADER : self.roll,
    # CHAT_HEADER : self.chat,
    # RESULT_HEADER : self.result,
    # TRACE_HEADER : self.trace,
    # VAR_HEADER : self.var

server = Server('127.0.0.1', 8000)
        # self.LOGFILE=sys.stdout #open('server.log', 'a')