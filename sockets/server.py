import socket, threading, time, datetime, sys, hashlib, random
from user import User
from room import Room, State
from communication import *

class Server:
    def __init__(self, HOST, PORT, LOGFILE=sys.stdout):
        self.HOST = HOST     # Standard loopback interface address (localhost)
        self.PORT = PORT     # Port to listen on (non-privileged ports are > 1023)
        self.rooms = {}
        self.LOGFILE = LOGFILE
        self.dispatch = {
            INIT_HEADER : self.init,
            ROLL_HEADER : self.roll,
            CHAT_HEADER : self.chat,
            RESULT_HEADER : self.result,
            TRACE_HEADER : self.trace,
            VAL_HEADER : self.val
        }
        self.run()

    def sender(self): #TODO: For testing purposes; Remove afterwards
        while True:
            action = input()
            if action == '1':
                message = 'CHAT|Player1|Catch me if u can\\'
            elif action == '2':
                message = 'ROLL|Player2\\' #TODO: Ideas for improvement: add involved players and die size
            elif action == '3':
                message = 'VAL|a8993|abc339\\'
            elif action == '4':
                message = 'RES|2|2|2|2\\'
            elif action == '5':
                message = 'RES|2|1|3|3|2\\'
            elif action == '6':
                message = 'TRC|Abc:12+22mod5=4|CDE:21-3mod7=4\\'
            elif action == '7':
                pass
            else:
                message = action
            
            for room in self.rooms.values():
                for player in room.get_players():
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
                    print('Over')
                    exit()

    def send_room(self, room, message, players = None):
        for player in room.get_players():
            if (players == None or player in players):
                player.conn.sendall(message) #TODO: Extend
    
    def send_message(self, player, message):
        player.conn.sendall(message)

    def list_players(self, room):
        lst = []
        for player in room.get_players():
            if player.is_GM:
                lst.append(f'{player.name} (GM)')
            elif player.name:
                lst.append(f'{player.name}')
        return ', '.join(lst)

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
            print(f'{datetime.datetime.now()} : Connected by {addr}', file=self.LOGFILE)
            try:
                while True:
                    data = conn.recv(128)
                    if not data:
                       break
                    self.handle(data, conn, user)
            except ConnectionResetError:
                print(f'ConnectionResetError: {addr} forcibly disconnected', file=self.LOGFILE)
            finally:
                #Remove the client from their room
                if user.room is not None: #TODO: What if gm leaves?
                    user.room.remove_player(user)
                    #If the room has been emptied
                    if not user.room.get_players():
                        del self.rooms[user.room.get_number()] #VOLATILE #or self.rooms.pop(user.room)

    def init(self, message, newUser):
        #INIT MESSAGE STRUCTURE ['INIT', '{room_number}', '{name}']
        room_number = message[1]
        username = message[2]
        if room_number in self.rooms:
            room = self.rooms[room_number]
            newUser.room = room
            room.add_player(newUser)
            for user in room.get_players():
                if user.name == username and user is not newUser:
                    # name taken TODO: collision elimination
                    username = str(username+"_"+hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5])
            newUser.name = username
            msg = f'{username} has joined the room!'
            self.send_room(room, compose(INFO_HEADER,[msg]))
            msg = f'Players in this room: {self.list_players(room)}'
            self.send_message(newUser, compose(INFO_HEADER,[msg]))
        else:
            room = Room(room_number)
            self.rooms[room_number] = room
            newUser.room = room
            newUser.name = username
            newUser.is_GM = True
            room.add_player(newUser)
            msg = f'You have joined the room {room.get_number()} as a GM\n'
            #TODO: msg+= "Use roll to roll"
            self.send_message(newUser, compose(INFO_HEADER,[msg]))

    def roll(self, message, user):
        room = user.room
        value = message[1]
        if True: #TODO: room.get_state() == State.ROLL:
            user.value = value
            room.values[user] = value
            if len(room.get_players()) == len(room.get_values()): 
                print(f'complete: {room.get_values()}') #TODO: roll stop and go on
                pass
            print(room.get_values())
        pass

    def chat(self, message, user):
        room = user.room
        self.send_room(room, message)
    
    def result(self, message, user):
        room = user.room
        result = message[1]
        if True: #TODO: if value.isnumeric():
            user.result = result
            room.results[user] = result
            if len(room.get_players()) == len(room.get_results()): 
                print(f'completeR: {room.get_results()}') #TODO: result stop and check         
                print(room.get_results())
            room.clear()
        pass

    def trace(self, message, user):
        room = user.room
        trace = message[1]
        if True: #TODO: if value.isnumeric():
            user.result = result
            room.results[user] = result
            if len(room.get_players()) == len(room.get_results()): 
                print(f'completeR: {room.get_results()}') #TODO: result stop and check         
                print(room.get_results())
            room.clear()
        pass

    def val(self, message, user):
        pass

server = Server('127.0.0.1', 8000)
        # self.LOGFILE=sys.stdout #open('server.log', 'a')