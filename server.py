import socket, threading, time, datetime, sys, hashlib, random, re, pyDHE
from user import User
from room import Room, State
from queue import Empty
from communication import *
from config import IPADDR, MAX_PLAYERS_PER_ROOM, MAX_STRING_LENGTH

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
            USER_LIST_HEADER : self.userList,
            ERROR_HEADER: self.error
        }
        self.run()

    def shutdown(self):
        print(f'Shutting down..')
        exit()

    def sender(self): #TODO: For testing purposes; Remove afterwards
        while True:
            action = input()
            if action == '1':
                message = 'CHAT|Player1|Generic message|Player2|Ans;;;'
            elif action == '2':
                message = 'ROLL|5|6;;;'
            elif action == '3':
                message = 'ROLL|a8993|abc339;;;'
            elif action == '4':
                message = 'RES|2|2;;;'
            elif action == '5':
                message = 'RES|2|1|3|3|2;;;'
            elif action == '6':
                message = 'TRC|Abc:12+22mod5=4|CDE:21-3mod7=4;;;'
            elif action == '7': #Get room 22 state; for State testing
                while True:
                    print(self.rooms['22'].get_state())
                    time.sleep(1)
                continue
            elif action == '8':
                message = 'ERR|VOE|somecoolval;;;'
            else:
                message = action
            for room in self.rooms.values():
                room.clear()
                room.start_action()
                for player in room.get_players():
                    message = encrypt(message.encode(), player.key)
                    player.conn.sendall(message)

    def run(self):
        print(f'Server up and running. Listening at {self.HOST}:{self.PORT}')
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
    def sendRoom(self, room, header, args, players = None):
        for player in room.get_players():
            if (players == None or player in players):
                msg = compose(header, args, player.key)
                player.conn.sendall(msg)

    def sendMessage(self, player, header, args):
        msg = compose(header, args, player.key)
        player.conn.sendall(msg)

    def chatBuffer(self, room):
        messages = []
        while True:
            if messages:
                self.sendRoom(room, CHAT_HEADER, messages)
                messages = []
            totalLength = sum([len(x) for x in messages])
            #TODO:config
            try:
                while totalLength < 800 and len(messages) < 10:
                    messages += room.messageQueue.get_nowait()
            except Empty:
                continue
            except:
                print(f'An unknown exception occured in chat buffer for room {room.room_number}. Perhaps you should restart the server')
            finally:
                time.sleep(0.4)

    def listPlayers(self, room):
        lst = []
        for player in room.get_players():
            if player.is_GM:
                lst.append(f'{player.name}(GM)')
            elif player.name:
                lst.append(f'{player.name}')
        return lst

    def handle(self, data, conn, user):
        messages = decompose(data, user.key)
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
        user.secret = pyDHE.new()
        user.sharedSecret = user.secret.negotiate(conn)
        salt = str(addr).encode()
        user.key = hashlib.pbkdf2_hmac('sha256', str(user.sharedSecret).encode(), salt, 100000)
        #TODO: better salt
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
                self.sendRoom(room, DROPPED_USER_HEADER, [name, int(user.is_GM)])
                self.sendRoom(room, USER_LIST_HEADER, self.listPlayers(room))

    def init(self, message, newUser):
        #INIT MESSAGE STRUCTURE ['INIT', '{room_number}', '{name}']
        #(For room assignment)  ['INIT', '', '{name}']
        if [item for item in message if len(item) > MAX_STRING_LENGTH]:
            self.sendMessage(newUser, ERROR_HEADER, [INPUT_TOO_LONG_ERROR])
            return
        if len(message) < 3:
            room_number = self.findRoomNumber()
            username  = message[1]
        else:
            room_number = message[1]
            username = message[2]
        if room_number in self.rooms:
            room = self.rooms[room_number]
            if len(room.get_players()) >= MAX_PLAYERS_PER_ROOM:
                self.sendMessage(newUser, ERROR_HEADER, [ROOM_FULL_ERROR])
                return
            newUser.room = room
            for user in room.get_players():
                if user.name == username and user is not newUser:
                    username = f'{username}_{self.getUsernameNumber(username, room.get_players())}'
                    break
            room.add_player(newUser)
            newUser.name = username
            self.sendMessage(newUser, INIT_HEADER, [room_number, username, 0])
        else:
            room = Room(room_number)
            self.rooms[room_number] = room
            threading.Thread(target=self.chatBuffer, args=(room,), daemon=True).start()
            newUser.room = room
            newUser.name = username
            newUser.is_GM = True
            room.add_player(newUser)
            self.sendMessage(newUser, INIT_HEADER, [room_number, username, 1])
        self.sendRoom(room, NEW_USER_HEADER, [username])
        self.sendRoom(room, USER_LIST_HEADER, self.listPlayers(room))

    def roll(self, message, user):
        room = user.room
        if user.is_GM:
            if room.get_state() is State.IDLE:
                if time.time() > room.nextRollAfter:
                    room.clear()
                    participants = self.getParticipants(room, message[3:]) #None if there's no player names if the message
                    room.start_action(participants)
                    room.set_state(State.ROLL)
                    timeout = int(message[1])
                    maxNum = int(message[2])
                    self.sendRoom(room, ROLL_HEADER, [timeout, maxNum], participants)
                else:
                    self.sendMessage(user, ERROR_HEADER, [ROLL_TOO_SOON_ERROR, round(time.time()-room.nextRollAfter)])
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
            self.sendRoom(room, VAL_HEADER, values)

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
        if len(room.get_participants()) == len(room.get_results()):
            print(f'DEBUG [RES]: All results received')
            results = room.get_results()
            room.set_state(State.IDLE)
            room.nextRollAfter = time.time()+5 if not room.problem else time.time()+15
            self.sendRoom(room, RESULT_HEADER, results)                      

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
            self.sendRoom(room, TRACE_HEADER, traces)

    def runSenderByState(self, state, room):
        return {
            State.ROLL : self.valSender,
            State.RESULT : self.resultSender,
            State.TRACE : self.traceSender 
        }[state](room)

    def userList(self, message, user):
        self.sendMessage(user, USER_LIST_HEADER, self.listPlayers(user.room))

    def error(self, message, user):
        #TODO: set room.problem
        pass
    #TODO: implement

    def getUsernameNumber(self, username, players):
        names = [player.name for player in players]
        pattern = re.compile(r'^{0}(_\d+)?$'.format(username))
        return sum([1 if pattern.match(name) else 0 for name in names])
    
    def findRoomNumber(self):
        i = 1
        while str(i) in self.rooms.keys():
            i += 1
        return f'{i}'

    def getParticipants(self, room, playerList):
        if not playerList:
            return None
        participants = []
        for player in room.get_players():
            if (player.name in playerList):
                participants.append(player)
        if len(playerList) != len(participants):
            print(f'[DEBUG] Some error in participant list: {playerList} submitted, but {[p.name for p in room.get_players()]} returned')
        return participants

    def chat(self, message, user):
        room = user.room
        room.messageQueue.put(message[1:])

server = Server(IPADDR, 8000)