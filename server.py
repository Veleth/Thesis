"""
Server module

Instance of Server class is responsible for server-side socket-based communication, relaying information and withholding inputs/results until every user has commited their values.
"""
import socket, threading, time, datetime, sys, hashlib, random, re, pyDHE
from user import User
from room import Room, State
from queue import Empty
from communication import *
from config import IPADDR, MAX_PLAYERS_PER_ROOM, MAX_STRING_LENGTH

class Server:
    """
    Server Class
    Attributes:
        HOST        server hostname
        PORT        port that server listens on
        rooms       the rooms on the server (instances of Room class)
        LOGFILE     file to which logs should be saved, sys.stdout by default
        dispatch    a dictionary with message headers as keys and functions as values
    """
    def __init__(self, HOST, PORT, LOGFILE=sys.stdout):
        """
        Server constructor
        Input: host address, socket port, logfile (sys.stdout by default)
        """
        self.HOST = HOST     
        self.PORT = PORT     # Port to listen on (non-privileged ports are > 1023)
        self.rooms = {}
        self.LOGFILE = LOGFILE
        self.dispatch = {
            INIT_HEADER : self.init,
            ROLL_HEADER : self.roll,
            CHAT_HEADER : self.chat,
            RESULT_HEADER : self.result,
            VAL_HEADER : self.val,
            USER_LIST_HEADER : self.userList,
            ERROR_HEADER: self.error
        }
        self.run()

    def shutdown(self):
        """
        Shuts the server down
        """
        print(f'Shutting down..')
        exit()

    def run(self):
        """
        Starts the server up and accepts connections, creating a thread for each new client
        """
        print(f'Server up and running. Listening at {self.HOST}:{self.PORT}')
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

    def sendRoom(self, room, header, args, players = None):
        """ 
        Sends a message to a given room
        Input:
            room        target room
            header      message header  
            args        message body
            players     list of recipients, if empty all players in the room are sent the message
        """
        for player in room.getPlayers():
            if (players == None or player in players):
                msg = compose(header, args, player.key)
                player.conn.sendall(msg)

    def sendMessage(self, player, header, args):
        """ 
        Sends a message to a given player
        Input:
            player      targetr player
            header      message header  
            args        message body
        """
        msg = compose(header, args, player.key)
        player.conn.sendall(msg)

    def chatBuffer(self, room):
        """
        Dequeues enqueued messages and sends them
        Input:
            room numbers
        """
        messages = []
        while True:
            if messages:
                self.sendRoom(room, CHAT_HEADER, messages)
                messages = []
            totalLength = sum([len(x) for x in messages])
            try:
                while totalLength < 800 and len(messages) < 10:
                    messages += room.messageQueue.get_nowait()
            except Empty:
                continue
            except:
                print(f'An unknown exception occured in chat buffer for room {room.getNumber()}. Perhaps you should restart the server')
            finally:
                time.sleep(0.4)

    def listPlayers(self, room):
        """
        Lists the players in a given room
        Input:
            room
        Output:
            stringified list of players in the room
        """
        lst = []
        for player in room.getPlayers():
            if player.is_GM:
                lst.append(f'{player.name}(GM)')
            elif player.name:
                lst.append(f'{player.name}')
        return lst

    def handle(self, data, conn, user):
        """
        Handles incoming messages, calling appropriate functions using the self.dispatch member
        Input: 
            data     incoming message
            conn     socket
            user     the second party in the communication 
        """
        messages = decompose(data, user.key)
        for message in messages:
            m = list(filter(None, message.split(MESSAGE_DELIMITER)))
            print(m)
            if m[0] in self.dispatch.keys():
                self.dispatch[m[0]](m, user)
            else:
                raise UndefinedHeaderException(m[0])

    def onNewConnection(self, conn, addr):
        """
        Called on each new connection. Negotiates the key and establishes communication.
        Input: 
            conn     socket
            addr     user address
        """
        user = User(conn, addr)
        conn.setblocking(True)
        user.secret = pyDHE.new()
        user.sharedSecret = user.secret.negotiate(conn)
        salt = str(addr).encode()
        user.key = hashlib.pbkdf2_hmac('sha256', str(user.sharedSecret).encode(), salt, 100000)
        with conn: #Start listening for messages
            print(f'{datetime.datetime.now()} : Connected by {addr}', file=self.LOGFILE)
            try:
                while True:
                    data = conn.recv(2048)
                    if not data:
                       break
                    self.handle(data, conn, user)
            except ConnectionResetError:
                print(f'{datetime.datetime.now()} : {addr} disconnected', file=self.LOGFILE)
            finally:
                self.endConnection(user)

    def endConnection(self, user):
        """
        Called on user disconnection
        Input:
            user     disconnected user
        """
        #Remove the client from their room
        room = user.room
        name = user.name
        if user.room is not None:
            state = room.getState()
            room.removePlayer(user)
            #If something is happening in the room
            if(state is not State.IDLE):
                self.runSenderByState(state, room)
            #If the room has been emptied
            if not user.room.getPlayers():
                del self.rooms[user.room.getNumber()]
            #Notify other players
            else:
                self.sendRoom(room, DROPPED_USER_HEADER, [name, int(user.is_GM)])
                self.sendRoom(room, USER_LIST_HEADER, self.listPlayers(room))

    def init(self, message, newUser):
        """
        Initializes the user on the server, setting their room and username as needed.
        Called when an init message is recieved.
        Input: message, user
        """
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
            if len(room.getPlayers()) >= MAX_PLAYERS_PER_ROOM:
                self.sendMessage(newUser, ERROR_HEADER, [ROOM_FULL_ERROR])
                return
            newUser.room = room
            for user in room.getPlayers():
                if user.name == username and user is not newUser:
                    username = f'{username}_{self.getUsernameNumber(username, room.getPlayers())}'
                    break
            room.addPlayer(newUser)
            newUser.name = username
            self.sendMessage(newUser, INIT_HEADER, [room_number, username, 0])
        else:
            room = Room(room_number)
            self.rooms[room_number] = room
            threading.Thread(target=self.chatBuffer, args=(room,), daemon=True).start()
            newUser.room = room
            newUser.name = username
            newUser.is_GM = True
            room.addPlayer(newUser)
            self.sendMessage(newUser, INIT_HEADER, [room_number, username, 1])
        self.sendRoom(room, NEW_USER_HEADER, [username])
        self.sendRoom(room, USER_LIST_HEADER, self.listPlayers(room))

    def roll(self, message, user):
        """
        Called when the GM calls for a roll.
        Input: message, user
        """
        room = user.room
        if user.is_GM:
            if room.getState() is State.IDLE:
                if time.time() > room.nextRollAfter:
                    room.clear()
                    participants = self.getParticipantList(room, message[3:]) #None if there are no player names in the message
                    room.startAction(participants)
                    room.setState(State.ROLL)
                    timeout = int(message[1])
                    maxNum = int(message[2])
                    self.sendRoom(room, ROLL_HEADER, [timeout, maxNum], participants)
                else:
                    self.sendMessage(user, ERROR_HEADER, [ROLL_TOO_SOON_ERROR, round(room.nextRollAfter-time.time())])
            else:
                print(f'ERROR [ROLL]: {message} recieved during state {room.getState()} in room {room.number}')
    
    def val(self, message, user):
        """
        Called when a value is recieved
        Input: message, user
        """
        room = user.room
        value = message[1]
        if room.getState() is State.ROLL and user in room.getParticipants():
            user.value = value
            room.values[user] = value
            self.valSender(room)
        else:
            print(f'ERROR [VAL]: {message} \nnot accepted for {user.name} in room {room.number}')
    
    def valSender(self, room):
        """
        Helper function for sending the values back at the right time
        Input: room
        """
        if len(room.getParticipants()) == len(room.getValues()):
            print(f'DEBUG [VAL]: All values received')
            values = room.getValues()
            room.setState(State.RESULT)
            self.sendRoom(room, VAL_HEADER, values, room.getParticipants())

    def result(self, message, user):
        """
        Called when a result is recieved
        Input: message, user
        """
        room = user.room
        result = message[1]
        if room.getState() is State.RESULT and result.isnumeric() and user in room.getParticipants():
            user.result = result
            room.results[user] = result
            self.resultSender(room)
        else:
            print(f'ERROR [RES]: {message} \nnot accepted for {user.name} in room {room.number}')

    def resultSender(self, room):
        """
        Helper function for sending the results back at the right time
        Input: room
        """
        if len(room.getParticipants()) == len(room.getResults()):
            print(f'DEBUG [RES]: All results received')
            results = room.getResults()
            room.setState(State.IDLE)
            room.nextRollAfter = time.time()+5 if not room.problem else time.time()+15
            self.sendRoom(room, RESULT_HEADER, results, room.getParticipants())                      

    def runSenderByState(self, state, room):
        """
        Helper function for running an appropriate helper function depending on room state
        Input: room, state
        Output:
            state-function dictionary
        """
        return {
            State.ROLL : self.valSender,
            State.RESULT : self.resultSender,
        }[state](room)

    def userList(self, message, user):
        """
        Sends a list of users upon request from a client
        Input: message, user
        """
        self.sendMessage(user, USER_LIST_HEADER, self.listPlayers(user.room))

    def error(self, message, user):
        """
        Reacts to error messages
        Input: message, user
        """
        room = user.room
        if user in room.getParticipants:
            room.problem = True
            self.sendRoom(room, ERROR_HEADER, message[1:])
        else:
            print(f'ERROR: [ERROR] {message} sent by a non-participant {user.name} in room {room.number}')

    def getUsernameNumber(self, username, players):
        """
        Helps with finding an unique username for a new user.
        Input:
            username    user-chosen username
            players     list of players in the room
        Output:
            a number that needs to be appended to make the username unique
        """
        names = [player.name for player in players]
        pattern = re.compile(r'^{0}(_\d+)?$'.format(username))
        return sum([1 if pattern.match(name) else 0 for name in names])
    
    def findRoomNumber(self):
        """
        Helps with finding an unique number for a new room
        """
        i = 1
        while str(i) in self.rooms.keys():
            i += 1
        return f'{i}'

    #Returns a list of user objects based on a list of strings
    def getParticipantList(self, room, playerList):
        """
        Returns a list of participants in a given room based on a list of strings
        Input: room, playerList
        Output:
            list of user objects
        """
        if not playerList:
            return None
        participants = []
        for player in room.getPlayers():
            if (player.name in playerList):
                participants.append(player)
        if len(playerList) != len(participants):
            print(f'[DEBUG] Some error in participant list: {playerList} submitted, but {[p.name for p in room.getPlayers()]} returned')
        return participants

    def chat(self, message, user):
        """
        Called when a chat message is recieved.
        Input: message, user
        """
        room = user.room
        room.messageQueue.put(message[1:])

server = Server(IPADDR, 8000)