import socket, time, threading, hashlib, sys, random
from communication import *

class Client:
    def __init__(self, HOST, PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.LOGFILE = open("app.log", "a") #TODO: Modify the values
        self.room = None
        self.max = None
        self.username = None
        self.ownValue = None
        self.ownResult = None
        self.ownTrace = None
        self.dispatch = {
            INIT_HEADER : self.init,
            ROLL_HEADER : self.roll,
            CHAT_HEADER : self.chat,
            RESULT_HEADER : self.result,
            VAL_HEADER : self.val,
            TRACE_HEADER : self.trace,
            INFO_HEADER : self.info
        }
        initializer = threading.Thread(target=self.init)
        initializer.start()
        # # initializer.join()
        threading.Thread(target=self.recv).start()
        # threading.Thread(target=self.send_loop).start()  

    def send_loop(self):
        self.sock.sendall(input().encode())

    def handle(self, data):
        messages = decompose(data)
        print(messages)
        for message in messages:
            m = list(filter(None, message.split(MESSAGE_DELIMITER)))
            if m[0] in self.dispatch.keys():
                self.dispatch[m[0]](m)
            else:
                raise UndefinedHeaderException(m[0])


    def recv(self):
        while True:
            data = self.sock.recv(128)
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

    """
    The following functions are responses to certain message headers and will be invoked
    when a message is recieved. The exception is init(), which is automatically called upon
    a successful connection.
    """

    """Initializes the user by selecting a room and username"""
    def init(self): #TODO: Later change to user-entered
        room = 22 #self.validated_input("Enter the number of the room: ")
        self.room = room
        username = str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5])#self.validated_input("Enter your username")    
        self.username = username
        message = compose(INIT_HEADER, [room, username])
        self.sock.sendall(message)
    
    """Call to roll by GM"""
    def roll(self, message): #TODO: Input and randomness, use the message
        self.print(f'INFO: A roll has been called, enter your random variable') 
        value = hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:8]#input()   
        print(value)
        message = compose(ROLL_HEADER, [value]) #TODO: randomize calculations
        self.sock.sendall(message)

    """Chat messages"""
    def chat(self, message):
        #CHAT MESSAGE STRUCTURE ['CHAT', "$player", "$chat_message"]
        self.print(f'{message[1]}: {message[2]}')

    """Players' results""" 
    def result(self):
        pass

    """Players' values"""
    def val(self, message):
        print(message)
        if True: #value in values:
            #calculate shiiiit
            result = 2
            message = compose(RESULT_HEADER, [result])
            self.sock.sendall(message)
        else:
            self.displayPrompt(f'ERROR: Your value {self.ownValue} not present in {message}')

    """Players' traces"""    
    def trace(self):
        pass

    """Info from server, handle basically like chat"""
    def info(self, message):
        #INFO MESSAGE STRUCTURE ['INFO', "$info_message" (1 or more)]
        self.print(f'INFO: {" ".join(message[1:])}')  


    """
    Client-GUI functionality that is called by the above functions.
    They serve as a bridge between the visual side and the backend of the application
    """

    def print(self, message):
        print(f'self print: {message}')
        #TODO: gui.display(format(msg))

    def getMsg(self):
        pass

    def getInput(self):
        pass

    def displayPrompt(self, prompt):
        print(f'prompt: {prompt}')
        pass


client = Client('127.0.0.1', 8000)