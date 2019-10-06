import socket, threading, time, datetime, sys, hashlib, random, re
from user import User
from room import Room, State
from communication import *

class Server:
    def __init__(self, HOST, PORT, LOGFILE=sys.stdout):
        self.HOST = HOST     
        self.PORT = PORT     # Port to listen on (non-privileged ports are > 1023)
        self.rooms = {}
        self.LOGFILE = LOGFILE
        self.dispatch = {
            INIT_HEADER : self.init,
            ROLL_HEADER : self.roll,
            CHAT_HEADER : self.chat,
            RESULT_HEADER : self.result,
            TRACE_HEADER : self.trace,
            VAL_HEADER : self.val,
            USER_LIST_HEADER : self.userList
        }
        self.run()

    def shutdown(self):
        print(f'Shutting down..')
        exit()

    def sender(self): #TODO: For testing purposes; Remove afterwards
        while True:
            action = input()
            if action == '1':
                message = 'CHAT|Player1|Generic message\\'
            elif action == '2':
                message = 'ROLL|5|6\\' #TODO: Ideas for improvement: add involved players
            elif action == '3':
                message = 'ROLL|a8993|abc339\\'
            elif action == '4':
                message = 'RES|2|2\\'
            elif action == '5':
                message = 'RES|2|1|3|3|2\\'
            elif action == '6':
                message = 'TRC|Abc:12+22mod5=4|CDE:21-3mod7=4\\'
            elif action == '7': #Get room 22 state; for State testing
                while True:
                    print(self.rooms['22'].get_state())
                    time.sleep(1)
                continue
            else:
                message = action
            for room in self.rooms.values():
                room.clear()
                room.start_action()
                for player in room.get_players():
                    player.conn.sendall(message.encode())

    def run(self):
        print(f'Server up and running. Listening at port {self.PORT}')
        threading.Thread(target=self.sender, daemon=True).start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setblocking(False)
            s.bind((self.HOST, self.PORT))
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=self.onNewConnection, args=(conn, addr), daemon=True).start()
                except BlockingIOError:
                    try:
                        time.sleep(1)
                    except (KeyboardInterrupt, SystemExit):
                        self.shutdown()
                except (KeyboardInterrupt, SystemExit):
                    self.shutdown()

    """ Sends message to a given room, optional parameter
    is the recipient list, by default everyone is a recipient """
    def sendRoom(self, room, message, players = None):
        for player in room.get_players():
            if (players == None or player in players):
                player.conn.sendall(message) #TODO: Extend
    
    def sendSeriesRoom(self, room, messages, players = None):
        for player in room.get_players():
            if (players == None or player in players):
                self.sendSeries(player, messages) #TODO: Extend

    def sendMessage(self, player, message):
        player.conn.sendall(message)

    def sendSeries(self, player, messages):
        for message in messages:
            self.sendMessage(player, message)

    def listPlayers(self, room):
        lst = []
        for player in room.get_players():
            if player.is_GM:
                lst.append(f'{player.name}(GM)')
            elif player.name:
                lst.append(f'{player.name}')
        return lst

    def handle(self, data, conn, user):
        messages = decompose(data)
        for message in messages:
            m = list(filter(None, message.split(MESSAGE_DELIMITER)))
            print(m)
            if m[0] in self.dispatch.keys():
                self.dispatch[m[0]](m, user)
            else:
                raise UndefinedHeaderException(m[0])

    def onNewConnection(self, conn, addr):
        user = User(conn, addr)
        conn.setblocking(True)
        with conn: #Start listening for messages
            print(f'{datetime.datetime.now()} : Connected by {addr}', file=self.LOGFILE)
            try:
                while True:
                    data = conn.recv(2048)
                    if not data:
                       break
                    self.handle(data, conn, user)
            except ConnectionResetError:
                print(f'ConnectionResetError: {addr} forcibly disconnected', file=self.LOGFILE)
            finally:
                self.endConnection(user)

    def endConnection(self, user):
        #Remove the client from their room
        room = user.room
        name = user.name
        if user.room is not None:
            state = room.get_state()
            room.remove_player(user)
            #If something is happening in the room
            if(state is not State.IDLE):
                self.runSenderByState(state, room)
            #If the room has been emptied
            if not user.room.get_players():
                del self.rooms[user.room.get_number()]
            #Notify other players
            else:
                self.sendRoom(room, compose(DROPPED_USER_HEADER, [name, int(user.is_GM)]))
                self.sendRoom(room, compose(USER_LIST_HEADER, self.listPlayers(room)))

    def init(self, message, newUser):
        #INIT MESSAGE STRUCTURE ['INIT', '{room_number}', '{name}']
        room_number = message[1]
        username = message[2]
        if room_number in self.rooms:
            room = self.rooms[room_number]
            newUser.room = room
            for user in room.get_players():
                if user.name == username and user is not newUser:
                    username = f'{username}_{self.getUsernameNumber(username, room.get_players())}'
                    break
            room.add_player(newUser)
            newUser.name = username
            self.sendMessage(newUser, compose(INIT_HEADER, [room_number, username, 0]))
        else:
            room = Room(room_number)
            self.rooms[room_number] = room
            newUser.room = room
            newUser.name = username
            newUser.is_GM = True
            room.add_player(newUser)
            self.sendMessage(newUser, compose(INIT_HEADER, [room_number, username, 1]))
        self.sendRoom(room, compose(NEW_USER_HEADER,[username]))
        self.sendRoom(room, compose(USER_LIST_HEADER, self.listPlayers(room)))

    def roll(self, message, user):
        room = user.room
        if user.is_GM:
            if room.get_state() is State.IDLE:
                room.clear()
                participants = message[3:] or None #None if there's no player names if the message
                room.start_action(participants)
                room.set_state(State.ROLL)
                timeout = int(message[1])
                maxNum = int(message[2])
                msg = compose(ROLL_HEADER, [timeout, maxNum])
                self.sendRoom(room, msg, participants)
            else:
                print(f'ERROR [ROLL]: {message} recieved during state {room.get_state()} in room {room}')
    
    def val(self, message, user):
        room = user.room
        value = message[1]
        if room.get_state() is State.ROLL and user in room.get_participants(): #TODO: timeout wait; maybe override in senders
            user.value = value
            room.values[user] = value
            self.valSender(room)
        else:
            print(f'ERROR [VAL]: {message} \nnot accepted for {user.name} in room {room}')
    
    def valSender(self, room):
        if len(room.get_participants()) == len(room.get_values()):
            print(f'DEBUG [VAL]: All values received')
            values = room.get_values()
            room.set_state(State.RESULT)
            self.sendRoom(room, compose(VAL_HEADER, values))

    def result(self, message, user):
        room = user.room
        result = message[1]
        if room.get_state() is State.RESULT and result.isnumeric() and user in room.get_participants(): #TODO: timeout wait
            user.result = result
            room.results[user] = result
            self.resultSender(room)
        else:
            print(f'ERROR [RES]: {message} \nnot accepted for {user.name} in room {room}')

    def resultSender(self, room):
        if len(room.get_participants()) == len(room.get_results()): #TODO: get participants
            print(f'DEBUG [RES]: All results received')
            results = room.get_results()
            room.set_state(State.IDLE) #TODO: Gather Traces?
            self.sendRoom(room, compose(RESULT_HEADER, results))                      

    def trace(self, message, user):
        room = user.room
        trace = message[1]
        if True: #TODO: state/user validation
            user.trace = trace
            room.traces[user] = trace
            self.traceSender(room)
        else:
            print(f'ERROR [TRACE]: {message} \nnot accepted for {user.name} in room {room}')

    def traceSender(self, room):
        if len(room.get_players()) == len(room.get_traces()): 
            print(f'DEBUG [TRACE]: All values received') #TODO: trace stop and send to all         
            traces = room.get_traces()
            # room.set_state(State.IDLE)
            self.sendRoom(room, compose(TRACE_HEADER, traces))

    def runSenderByState(self, state, room):
        return {
            State.ROLL : self.valSender,
            State.RESULT : self.resultSender,
            State.TRACE : self.traceSender 
        }[state](room)

    def userList(self, message, user):
        self.sendMessage(user, compose(USER_LIST_HEADER, self.listPlayers(user.room)))

    def getUsernameNumber(self, username, players):
        names = [player.name for player in players]
        pattern = re.compile(r'^{0}(_\d+)?$'.format(username))
        return sum([1 if pattern.match(name) else 0 for name in names])

    def chat(self, message, user):
        room = user.room
        message = compose(CHAT_HEADER, message[1:])
        self.sendRoom(room, message)

server = Server(IPADDR, 8000)