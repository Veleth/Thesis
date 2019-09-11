import socket, time, threading, hashlib, sys, random
from communication import *
from collections import Counter

class Client:
    def __init__(self, HOST, PORT, username, room, gui=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui = gui
        self.sock.connect((HOST, PORT))
        self.room = room
        self.username = username
        self.ownValue = None
        self.ownResult = None
        self.ownTrace = None
        self.traces = []
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
    def init(self): #TODO: Later change to user-entered
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
        print(message)
        if True: #value in values:
            #calculate stuff, create trace
            result = 2 #TODO: remove temporary stub
            self.ownResult = result
            self.ownTrace = 'avavav'
            message = compose(RESULT_HEADER, [self.ownResult])
            message += compose(TRACE_HEADER, [self.ownTrace])
            self.sock.sendall(message)
        else:
            self.displayPrompt(f'ERROR: Your value {self.ownValue} not present in {message}')

    """Players' traces"""    
    def trace(self, message):
        for trace in message[1:]:
            self.traces += trace 
        pass

    """Info from server, handle basically like chat"""
    def info(self, message):
        #INFO MESSAGE STRUCTURE ['INFO', "$info_message" (1 or more)]
        self.print(f'INFO: {" ".join(message[1:])}')  


    """
    Client-GUI functionality that is called by the above functions.
    They serve as a bridge between the visual side and the backend of the application.
    They are also useful for decoupling GUI for testing purposes.
    """

    def print(self, message):
        if self.gui:
            pass
            #TODO: gui.display(format(msg))
        else:
            print(f'self print: {message}')

    def getMsg(self):
        if self.gui:
            pass
            #TODO: gui.getfromfield
        else:
            pass
            #some input()

    def getInput(self):
        if self.gui:
            pass
            #TODO: gui.getfromfield
        else:
            pass
            #some input()

    def displayPrompt(self, prompt):
        if self.gui:
            pass
            #TODO: gui.prompt
        else:
            print(f'prompt: {prompt}')

#TODO: Remove later
if __name__=='__main__':
    client = Client('127.0.0.1', 8000, username = str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]), room=22)