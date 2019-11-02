import socket, time, threading, hashlib, sys, random, datetime, pyDHE, logging
from communication import *
from config import *
from calculator import method1 as calculate
from collections import Counter

class Client:
    def __init__(self, HOST, PORT, username, room, gui=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui = gui
        self.sock.connect((HOST, PORT))
        self.room = room
        self.username = username
        self.maxNum = 0
        self.isGM = False
        self.ownValue = None
        self.ownResult = None
        self.ownTrace = None
        self.rollTime = None
        self.rng = random.SystemRandom()
        self.traces = []
        self.dispatch = {
            INIT_HEADER : self.init,
            ROLL_HEADER : self.roll,
            CHAT_HEADER : self.chat,
            RESULT_HEADER : self.result,
            VAL_HEADER : self.val,
            TRACE_HEADER : self.trace,
            INFO_HEADER : self.info,
            NEW_USER_HEADER : self.newUser,
            DROPPED_USER_HEADER : self.droppedUser,
            USER_LIST_HEADER : self.userList,
            ERROR_HEADER: self.error
        }
        negotiator = threading.Thread(target=self.negotiate, daemon=True)
        negotiator.start()
        negotiator.join()
        initializer = threading.Thread(target=self.initialize, daemon=True)
        initializer.start()
        threading.Thread(target=self.recv, daemon=True).start()
        #TODO: daemon false if problems with recv or client shuts down
    
    def negotiate(self):
        self.secret = pyDHE.new()
        self.sharedSecret = self.secret.negotiate(self.sock)
        salt = str(self.sock.getsockname()).encode()
        self.key = hashlib.pbkdf2_hmac('sha256', str(self.sharedSecret).encode(), salt, 100000)
        
    def initialize(self):
        message = compose(INIT_HEADER, filter(None, [self.room, self.username]), self.key)
        self.sock.sendall(message)

    def handle(self, data):
        messages = decompose(data, self.key)
        for message in messages:
            try:
                m = list(filter(None, message.split(MESSAGE_DELIMITER)))
                if m[0] in self.dispatch.keys():
                    self.dispatch[m[0]](m)
                else:
                    raise UndefinedHeaderException(m[0])
            except:
                logging.exception('ClientHandleError')

    def recv(self): #TODO: change to non-blocking
        try:
            while True:
                data = self.sock.recv(2048)
                if not data:
                    break
                self.handle(data)
        except ConnectionResetError:
            self.gui.logout()
            self.gui.showerror('Connection lost', 'You have lost connection to the server.\nIt might have shut down.')
        except ConnectionAbortedError:
            self.gui.showinfo('Logout', 'You have successfully logged out!')
        except:
            logging.exception('RecvUnhandledException')
        finally:
            print('Stopped accepting incoming messages')

    def validated_input(self, message):
        ans = input(message)
        while not ans.isalnum():
            print("Wrong! Only alphanumeric non-empty strings allowed. Try again!")
            ans = input(message)
        return ans

    def validated_chat(self, message):
        return message.replace(MESSAGE_END, '').replace(MESSAGE_DELIMITER, '')

    def clear(self):
        self.ownValue = None
        self.ownResult = None
        self.ownTrace = None
        self.traces = []


    """
    The following functions are responses to certain message headers and will be invoked
    when a message is recieved. The exception is init(), which is automatically called upon
    a successful connection.
    """

    """Initializes the user by selecting a room and username"""
    def init(self, message):
        self.room = message[1]
        self.username = message[2]
        if self.gui:
            self.gui.checkNameChange(message[2])
        self.isGM = bool(int(message[3]))
        if self.isGM:
            self.gui.prepareCommandFrame()
        self.gui.refreshHeader()
    
    """Call to roll by GM"""
    def roll(self, message):
        #server -> client ['ROLL', '{timeout}', '{maxNum}']
        self.print(f'INFO: A roll has been called, enter your random variable') 
        self.rollTime = datetime.datetime.now()
        timeout,  maxNum = message[1:]
        self.maxNum = int(maxNum)
        self.getInput(int(timeout), int(maxNum))

    """Chat messages"""
    def chat(self, message):
        #server -> client ['CHAT', '{player}', '{chat_message}']
        #server -> client ['CHAT', '{player}', '{chat_message}', '{player}', '{chat_message}', ...]
        if len(message) > 3:
            #Create an array of tuples (player_name, chat_message)
            for player_name,chat_message in zip(message[1::2], message[2::2]):
                self.print(f'{player_name}: {chat_message}')
        else:
            self.print(f'{message[1]}: {message[2]}')

    """Players' results""" 
    def result(self, message):
        #server -> client ['RES', '{result1}', '{result2}', ...]
        results = [int(res) for res in message[1:]]
        if self.ownResult in results:   # If our value is in results
            if (len(set(results)) == 1):  # If all results are the same
                self.print(f'The result is {self.ownResult}')
            else:
                self.print(f'Something went wrong and not everyone has the same result. They are as follows (result: number of occurences): {dict(Counter(results))}')
        else:
            self.print(f'Your result {self.ownResult} is not present in results from server: {results}')
            msg = compose(ERROR_HEADER, [RESULT_DIFFERS_ERROR, self.ownResult], self.key)
            self.sock.sendall(msg)
        pass

    """Players' values"""
    def val(self, message):
        values = message[1:]
        if self.ownValue in values:
            self.ownResult, self.ownTrace = calculate(values, self.maxNum)
            self.print(f'Your calculation: {self.ownResult}')
            message = compose(RESULT_HEADER, [self.ownResult], self.key)
            self.sock.sendall(message)
        else:
            self.showwarning('Value not present', f'Your value {self.ownValue} not present in {message}. The server has been notified.')
            msg = compose(ERROR_HEADER, [VALUE_OMITTED_ERROR, self.ownValue], self.key)
            self.sock.sendall(msg)

    """Players' traces"""    
    def trace(self, message):
        for trace in message[1:]:
            self.traces += trace 
        pass #TODO: decide

    def userList(self, message):
        users = message[1:]
        self.gui.setUserList(users)

    def error(self, message):
        if message[1] in [VALUE_OMITTED_ERROR, RESULT_DIFFERS_ERROR]:
            title = 'Calculation problem'
            contents = f'There has been an error during calculations.\nDo you want to save your trace?'
            if self.askquestion(title, contents) == 'yes':
                with open('trace.txt', 'a') as f:
                    f.write(f'---------------\nRoll start: {self.rollTime}\nYour value: {self.ownValue}\n{self.ownTrace}\n')
                self.showinfo('Success', 'Trace successfully saved!')
        pass #TODO: fix, refine, complete, split

    """Info from server, handle basically like chat"""
    def info(self, message):
        #INFO MESSAGE STRUCTURE ['INFO', "$info_message" (1 or more)]
        self.print(f'INFO: {" ".join(message[1:])}')  

    def newUser(self, message):
        username = message[1]
        self.print(f'INFO: {username} has joined the room')

    def droppedUser(self, message):
        username = message[1]
        if int(message[2]):
            self.print(f'INFO: {username} (GM) has left the room.\nYou can keep chatting with others, but no further rolls will be made.')
        else:
            self.print(f'INFO: {username} has left the room.')
        

    """
    Client-GUI functionality that is called by the above functions.
    They serve as a bridge between the visual side and the backend of the application.
    They are also useful for decoupling GUI for testing purposes.
    """

    def print(self, message):
        if self.gui:
            self.gui.print(message)
        else:
            print(f'Text Area Print: {message}')

    def getInput(self, timeout, maxNum):
        if self.gui:
            self.gui.getUserValue(timeout, maxNum)
        else:
            pass 

    def askquestion(self, title, message):
        return self.gui.askquestion(title, message)

    def showerror(self, title, message):
        self.gui.showerror(title, message)

    def showwarning(self, title, message):
        self.gui.showwarning(title, message)

    def showinfo(self, title, message):
        self.gui.showinfo(title, message)

    """
    Client functionality called by the GUI
    """

    def sendChat(self, message):
        #TODO: remove DDOS test
        # for i in range(1,1000):
        #     msg = compose(CHAT_HEADER, [self.username, f'{message}{i}'], self.key)
        #     self.sock.sendall(msg)
        #     time.sleep(0.01)
        msg = compose(CHAT_HEADER, [self.username, message], self.key)
        self.sock.sendall(msg)

    def sendValue(self, seed):
        self.ownValue = hashlib.sha256(f'{time.time()}{self.rng.random()}{seed}'.encode()).hexdigest()
        message = compose(VAL_HEADER, [self.ownValue], self.key)
        self.print(f'DEBUG: value sent - {self.ownValue}')
        self.sock.sendall(message)
        return self.ownValue

    def getRandomValue(self):
        if self.ownValue:
            return hashlib.sha256(f'{time.time()}{self.rng.random()}{self.ownValue}'.encode()).hexdigest() 
        return hashlib.sha256(f'{self.rng.random()}{time.time()}{self.rng.random()}'.encode()).hexdigest()

    def startRoll(self, timeout, maxNum, participants):
        #client -> server ['ROLL', '{timeout}', '{maxNum}', '{participant}', '{participant}', ...]
        args = [timeout, maxNum] + participants if participants else [timeout, maxNum]
        message = compose(ROLL_HEADER, args, self.key)
        self.sock.sendall(message)