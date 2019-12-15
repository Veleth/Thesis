"""
Client module

Instance of Client class is responsible for client-side socket-based communication, and low-level basic program functionality
"""
import socket, time, threading, hashlib, sys, random, datetime, pyDHE, logging
from communication import *
from config import *
from calculator import method1 as calculate
from collections import Counter

class Client:
    """
    Client Class - abstraction for a socket client.
    Attributes:
        sock        socket object
        gui         reference to GUI object (for transferring messages to UI)
        room        current room of the user
        username    current username of the user
        maxnum      max number in the current calculations, initially None
        isGM        whether the user is a GM
        ownValue    current user individual value
        ownResult   current user individual result
        ownTrace    current user individual computation trace
        rollTime    time of the last roll
        rng         random number generator for the user
        dispatch    a dictionary with message headers as keys and functions as values
    """
    def __init__(self, HOST, PORT, username, room, gui=None):
        """
        Client constructor
        Input: host address, socket port, user-chosen username and room number.
        Also a GUI reference, which in this implementation is a Tkinter object.
        """
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
        self.dispatch = {
            INIT_HEADER : self.init,
            ROLL_HEADER : self.roll,
            CHAT_HEADER : self.chat,
            RESULT_HEADER : self.result,
            VAL_HEADER : self.val,
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
    
    def negotiate(self):
        """
        Negotiates a Diffie-Hellman key with the server
        """
        self.secret = pyDHE.new()
        self.sharedSecret = self.secret.negotiate(self.sock)
        salt = str(self.sock.getsockname()).encode()
        self.key = hashlib.pbkdf2_hmac('sha256', str(self.sharedSecret).encode(), salt, 100000)
        
    def initialize(self):
        """
        Sends an initialization request to the server, along with user name and room)
        """
        message = compose(INIT_HEADER, filter(None, [self.room, self.username]), self.key)
        self.sock.sendall(message)

    def handle(self, data):
        """
        Handles incoming messages, calling appropriate functions using the self.dispatch member
        Input: 
            data     incoming message
        """
        messages = decompose(data, self.key)
        for message in messages:
            print(message) #TODO: remove
            try:
                m = list(filter(None, message.split(MESSAGE_DELIMITER)))
                if m[0] in self.dispatch.keys():
                    self.dispatch[m[0]](m)
                else:
                    raise UndefinedHeaderException(m[0])
            except:
                logging.exception('ClientHandleError')

    def recv(self):
        """
        Runs on a dedicated thread, constantly listening on the socket and calling handle() on received messages.
        """
        try:
            while True:
                data = self.sock.recv(2048)
                if not data:
                    break
                self.handle(data)
        except ConnectionResetError:
            self.gui.logout()
            self.gui.showError('Connection lost', 'You have lost connection to the server.\nIt might have shut down.')
        except ConnectionAbortedError:
            self.gui.showInfo('Logout', 'You have successfully logged out!')
        except:
            logging.exception('RecvUnhandledException')
            self.gui.logout(alert='An unexpected connection error has occured. You have been logged out.')
        finally:
            print('Communication with the server was lost.')

    def clear(self):
        """
        Clears stored value, result, and trace for the next roll.
        """
        self.ownValue = None
        self.ownResult = None
        self.ownTrace = None


    #The following functions are responses to certain message headers and will be invoked
    #when a message is recieved. The exception is init(), which is automatically called upon
    #a successful connection.
    
    def init(self, message):
        """
        Initializes the user locally, adjusting their room and username as needed.
        Called when an init message is recieved.
        Input: message
        """
        self.room = message[1]
        self.username = message[2]
        if self.gui:
            self.gui.checkNameChange(message[2])
        self.isGM = bool(int(message[3]))
        if self.isGM:
            self.gui.addGmElements()
        self.gui.refreshHeader()
    
    def roll(self, message):
        """
        Called when the GM calls for a roll.
        Input: message
        """
        timeout,  maxNum = message[1:]
        self.print(f'INFO: A roll has been called (1-{maxNum}), enter your random variable') 
        self.rollTime = datetime.datetime.now()
        self.maxNum = int(maxNum)
        self.getInput(int(timeout), int(maxNum))

    def chat(self, message):
        """
        Called when a chat message is recieved.
        Input: message
        """
        if len(message) > 3:
            #Create an array of tuples (player_name, chat_message)
            for player_name,chat_message in zip(message[1::2], message[2::2]):
                self.print(f'{player_name}: {chat_message}')
        else:
            self.print(f'{message[1]}: {message[2]}')

    def result(self, message):
        """
        Called when the results come back from the server
        Input: message
        """
        results = [int(res) for res in message[1:]]
        if self.ownResult in results:
            if (len(set(results)) == 1):
                self.print(f'The result is {self.ownResult}')
            else:
                self.print(f'Something went wrong and not everyone has the same result. They are as follows (result: number of occurences): {dict(Counter(results))}')
        else:
            self.print(f'Your result {self.ownResult} is not present in results from server: {results}')
            msg = compose(ERROR_HEADER, [RESULT_DIFFERS_ERROR, self.ownResult], self.key)
            self.sock.sendall(msg)
        pass

    def val(self, message):
        """
        Called when the values come back from the server
        Input: message
        """
        values = message[1:]
        if self.ownValue in values:
            self.ownResult, self.ownTrace = calculate(values, self.maxNum)
            self.print(f'Your calculation: {self.ownResult}')
            message = compose(RESULT_HEADER, [self.ownResult], self.key)
            self.sock.sendall(message)
        else:
            self.showWarning('Value not present', f'Your value {self.ownValue} not present in {message}. The server has been notified.')
            msg = compose(ERROR_HEADER, [VALUE_OMITTED_ERROR, self.ownValue], self.key)
            self.sock.sendall(msg)

    def userList(self, message):
        """
        Called when the list of users in the room needs to be updated.
        Input: message
        """
        users = message[1:]
        self.gui.setUserList(users)

    def error(self, message):
        """
        Called when an error message is received.
        Input: message
        """
        if message[1] in [VALUE_OMITTED_ERROR, RESULT_DIFFERS_ERROR]:
            title = 'Calculation problem'
            contents = f'There has been an error during calculations.\nDo you want to save your trace?'
            if self.askQuestion(title, contents) == 'yes':
                with open('trace.txt', 'a') as f:
                    f.write(f'---------------\nRoll start: {self.rollTime}\nYour value: {self.ownValue}\n{self.ownTrace}\n')
                self.showInfo('Success', 'Trace successfully saved!')
        elif message[1] == ROLL_TOO_SOON_ERROR:
            self.print(f'You tried rolling too soon. Try waiting {message[2]}s.')
        elif message[1] in [INPUT_TOO_LONG_ERROR, ROOM_FULL_ERROR]:
            msg = 'The selected room is full, try again later' if message[1] == ROOM_FULL_ERROR else 'A string you entered was too long, please try logging in with different data'
            self.gui.logout(msg)

    def info(self, message):
        """
        Called when information from server is recieved. Similar to chat.
        Input: message
        """
        self.print(f'INFO: {" ".join(message[1:])}')  

    def newUser(self, message):
        """
        Called when an user joins the room
        Input: message
        """
        username = message[1]
        self.print(f'INFO: {username} has joined the room')

    def droppedUser(self, message):
        """
        Called when an user leaves the room
        Input: message
        """
        username = message[1]
        if int(message[2]):
            self.print(f'INFO: {username} (GM) has left the room.\nYou can keep chatting with others, but no further rolls will be made.')
        else:
            self.print(f'INFO: {username} has left the room.')
        

    
    # Client-GUI functionality that is called by the above functions.
    # They serve as a bridge between the visual side and the backend of the application.
    # They are also useful for decoupling GUI for testing purposes.

    def print(self, message):
        """
        Prints input text to textbox in the GUI
        Input: string to be printed
        """
        if self.gui:
            self.gui.print(message)
        else:
            print(f'Text Area Print: {message}')

    def getInput(self, timeout, maxNum):
        """
        Called when user input is required.
        Input: 
            timeout     how much time the user has to enter the input
            maxNum      what max number in the calculations is
        """
        if self.gui:
            self.gui.getUserValue(timeout, maxNum)
        else:
            pass 

    def askQuestion(self, title, message):
        """
        Opens a question box in the GUI with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        return self.gui.askQuestion(title, message)

    def showError(self, title, message):
        """
        Opens an error box in the GUI with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        self.gui.showError(title, message)

    def showWarning(self, title, message):
        """
        Opens a warning box in the GUI with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        self.gui.showWarning(title, message)

    def showInfo(self, title, message):
        """
        Opens an info box in the GUI with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        self.gui.showInfo(title, message)

    #
    #Client functionality called by the GUI
    #

    def sendChat(self, message):
        """
        Called by the GUI to send a message over chat.
        Input: message to be sent
        """
        msg = compose(CHAT_HEADER, [self.username, message], self.key)
        self.sock.sendall(msg)

    def sendValue(self, seed):
        """
        Called by the GUI to send a value to the server.
        Input: seed for calculating the value
        Output: the value submitted by the user
        """
        self.ownValue = hashlib.sha256(f'{time.time()}{self.rng.random()}{seed}'.encode()).hexdigest()
        message = compose(VAL_HEADER, [self.ownValue], self.key)
        # self.print(f'DEBUG: value sent - {self.ownValue}')
        self.sock.sendall(message)
        return self.ownValue

    def getRandomValue(self):
        """
        Called by the GUI to send a random value to the server.
        Output: the value submitted by the user
        """
        if self.ownValue:
            return hashlib.sha256(f'{time.time()}{self.rng.random()}{self.ownValue}'.encode()).hexdigest() 
        return hashlib.sha256(f'{self.rng.random()}{time.time()}{self.rng.random()}'.encode()).hexdigest()

    def startRoll(self, timeout, maxNum, participants):
        """
        Called by the GUI to start a roll in the room.
        For GM only.
        Input: 
            timeout         max timeout allowed for the participants
            maxNum          max number that can be calculated in the roll
            participants    list of participants. If empty, everyone in the room takes part
        """
        args = [timeout, maxNum] + participants if participants else [timeout, maxNum]
        message = compose(ROLL_HEADER, args, self.key)
        self.sock.sendall(message)