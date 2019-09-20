import socket, time, threading, hashlib, sys, random
from communication import *
from collections import Counter

class Client:
    def __init__(self, HOST, PORT, username, room, gui=None):
        #TODO: Add GM indication
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui = gui
        self.sock.connect((HOST, PORT))
        self.room = room
        self.username = username
        self.maxNum = 0 # Current max roll
        self.isGM = False
        self.ownValue = None
        self.ownResult = None
        self.ownTrace = None
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
            USER_LIST_HEADER : self.userList
        }
        initializer = threading.Thread(target=self.initialize, daemon=True)
        initializer.start()
        threading.Thread(target=self.recv, daemon=False).start()

    def initialize(self):
        message = compose(INIT_HEADER, [self.room, self.username])
        self.sock.sendall(message)

    def handle(self, data):
        messages = decompose(data)
        print(messages)
        for message in messages:
            try:
                m = list(filter(None, message.split(MESSAGE_DELIMITER)))
                if m[0] in self.dispatch.keys():
                    self.dispatch[m[0]](m)
                else:
                    raise UndefinedHeaderException(m[0])
            except:
                exit(2)

    def recv(self): #TODO: change to non-blocking
        while True:
            data = self.sock.recv(2048) #TODO: change if 
            if not data:
                break
            self.handle(data)
        print("An error has occured")

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

    def calculate(self, values, maxNum): #TODO: improve and refine
        s = sum([int(v, 16) for v in values])
        self.ownResult = s%maxNum or maxNum #if 0 then maxNum
        print(f'Result: {self.ownResult}')
        #TODO: Clarify in the string
        self.ownTrace = f'The values: {values}\n, the sum: {s}, mod {maxNum} equals to {self.ownResult}'

    """
    The following functions are responses to certain message headers and will be invoked
    when a message is recieved. The exception is init(), which is automatically called upon
    a successful connection.
    """

    """Initializes the user by selecting a room and username"""
    def init(self, message): # TODO: Handle errors etc
        self.room = message[1]
        self.username = message[2]
        self.isGM = bool(int(message[3]))
        breakpoint()
        print(message)
        pass        
    
    """Call to roll by GM"""
    def roll(self, message):
        self.print(f'INFO: A roll has been called, enter your random variable') 
        timeout,  maxNum = message[1:]
        self.maxNum = int(maxNum)
        self.getInput(int(timeout), int(maxNum))

    """Chat messages"""
    def chat(self, message):
        #server -> client ['CHAT', "$player", "$chat_message"]
        self.print(f'{message[1]}: {message[2]}')

    """Players' results""" 
    def result(self, message):
        #server -> client ['RES', '{result1}', '{result2}', ...]
        results = [int(res) for res in message[1:]]
        if self.ownResult in results:   # If our value is in results
            if (len(set(results)) == 1):  # If all results are the same #TODO: possibly move functionality to server
                self.print(f'The result is {self.ownResult}')
            else:
                self.print(f'Something went wrong and not everyone has the same result. They are as follows (result: number of occurences): {dict(Counter(results))}')
                #str(dict).replace(', ','\r\n').replace("u'","").replace("'","")[1:-1] or https://stackoverflow.com/questions/17330139/python-printing-a-dictionary-as-a-horizontal-table-with-headers
        else:
            self.print(f'Your result {self.ownResult} is not present in results from server: {results}')
        pass

    """Players' values"""
    def val(self, message):
        values = message[1:]
        if True: #TODO value in values:
            self.calculate(values, self.maxNum)
            message = compose(RESULT_HEADER, [self.ownResult])
            self.sock.sendall(message)
        else:
            self.print(f'ERROR: Your value {self.ownValue} not present in {message}')

    """Players' traces"""    
    def trace(self, message):
        for trace in message[1:]:
            self.traces += trace 
        pass

    def userList(self, message):
        users = message[1:]
        self.gui.setUserList(users)
        #TODO: remove
        self.print(f'User list: {users}')

    """Info from server, handle basically like chat"""
    def info(self, message):
        #INFO MESSAGE STRUCTURE ['INFO', "$info_message" (1 or more)]
        self.print(f'INFO: {" ".join(message[1:])}')  

    def newUser(self, message):
        username = message[1]
        self.print(f'INFO: {username} has joined the room')

    def droppedUser(self, message):
        username = message[1]
        self.print(f'INFO: {username} has left the room')

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

    """
    Client functionality called by the GUI
    """

    def sendChat(self, message):
        print(f'Chatsend message {message}')
        message = compose(CHAT_HEADER, [self.username, message])
        self.sock.sendall(message)

    def sendValue(self, seed):
        self.ownValue = hashlib.sha256(f'{time.time()}{self.rng.random()}{seed}'.encode()).hexdigest()
        message = compose(VAL_HEADER, [self.ownValue])
        self.print(f'DEBUG: value sent - {self.ownValue}')
        self.sock.sendall(message)

    def getRandomValue(self):
        if self.ownValue:
            return hashlib.sha256(f'{time.time()}{self.rng.random()}{self.ownValue}'.encode()).hexdigest() 
        return hashlib.sha256(f'{self.rng.random()}{time.time()}{self.rng.random()}'.encode()).hexdigest()

#TODO: Remove later
if __name__=='__main__':
    client = Client(IPADDR, 8000, username = str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]), room=22)