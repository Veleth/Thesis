"""
Gui module

Instance of GUI class is responsible for direct user interaction
"""
from tkinter import *
from tkinter import messagebox
from client import Client
import threading, logging
from communication import *
from config import IPADDR, MIN_USERNAME_CHARS, MAX_USERNAME_CHARS, MIN_ROOM_NUMBER_CHARS, MAX_ROOM_NUMBER_CHARS

class GUI():
    """
    GUI Class - responisble for the main window of the GUI
    Attributes:
        window        Tk class object, main window of the app
        _frame        currently displayed frame
        client        reference to Client class
    """
    def __init__(self):
        """
        Initializes basic window
        """
        self.window = Tk()
        self.window.title('RPG player companion app')
        self.window.resizable(False,False)
        self.window.protocol('WM_DELETE_WINDOW', self.exit)
        canvas = Canvas(self.window, height=360, width=360)
        canvas.pack()
        
        self._frame = None
        self.switchFrame(LoginFrame)
        self.window.mainloop()

    def launchClient(self, host, port, username, room):
        """
        Attempts to create a client and change frame to ApplicationFrame
        Input:
            host        target server hostname
            port        target server port
            username    user-selected username
            room        user-selected room
        """
        try:
            self.switchFrame(ApplicationFrame)
            self.window.geometry('480x720')
            self.client = Client(host, int(port), username, room, gui=self)
        except:
            self.window.geometry('360x360')
            self.host = host
            self.port = port
            self.username = username
            self.room = room
            messagebox.showerror('Connection error', f'Host {host} is not responding on port {port}\nMake sure the information is correct and the server is properly configured')
            self.switchFrame(LoginFrame)

    def switchFrame(self, frame_class):
        """
        Changes active frame for GUI
        Input:
            frame_class     target frame class
        """
        new_frame = frame_class(self.window, self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame 
        self._frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def print(self, message):
        """
        Prints a message from client to textbox in the frame
        Input: 
            message     message to be printed
        """
        if isinstance(self._frame, ApplicationFrame):
            self._frame.print(message)

    def sendChat(self, message):
        """
        Sends a chat message to the client
        Input: 
            message     message to be sent
        """
        maxLength = 140
        self.client.sendChat(message[:maxLength])
    
    def sendValue(self, value):
        """
        Sends a value to the client
        Input: 
            value     user-created value
        """
        return self.client.sendValue(value)

    def refreshHeader(self):
        """
        Refreshes the header in the Application Frame.
        """
        if isinstance(self._frame, ApplicationFrame):
            self._frame.setHeader(self.getHeader())

    def getHeader(self):
        """
        Fetches user information header for Application Frame
        Output: header with user information
        """
        return f'{self.client.username} (GM) - Room {self.client.room}' if self.client.isGM else f'{self.client.username} - Room {self.client.room}'

    def isGM(self):
        """
        Checks if client is a GM
        Output: boolean
        """
        return self.client.isGM

    def getTrace(self):
        """
        Fetches user calculation trace
        Output: User calculation trace
        """
        if self.client.ownResult:
            return f'Roll start: {self.client.rollTime}\nYour value: {self.client.ownValue}\n{self.client.ownTrace}'
        else:
            return f'No calculations have taken place yet.\nWait for others to submit their values.'
    
    def getUserValue(self, timeout, maxNum):
        """
        Calls appropriate functions and starts a timeout to get user value
        Input:
            timeout        time for the user to enter value
            maxNum         max number that can be calculated in the roll
        """
        if isinstance(self._frame, ApplicationFrame):
            thread = threading.Thread(target=self._frame.getUserValue, daemon=True)
            thread.start()
            thread.join(timeout=timeout)
            if self._frame.entryDone.get():
                pass
            else:
                self._frame.sendValue(self.client.getRandomValue())

    def addGmElements(self):
        """
        Adds GM-only elements in the Application Frame
        """
        if isinstance(self._frame, ApplicationFrame):
            self._frame.addGmElements() 

    def setUserList(self, users):
        """
        Refreshes the list of users in the Application Frame
        Input: 
            users       list of users
        """
        if isinstance(self._frame, ApplicationFrame):
            self._frame.setUserList(users)

    def startRoll(self, timeout, maxNum, participants):
        """
        Calls client function that starts the roll
        Input: 
            timeout         timeout for the roll
            maxNum          max number in the roll
            participants    roll participants
        """
        self.client.startRoll(timeout, maxNum, participants)

    def exit(self):
        """
        Exits the program, closing the client socket
        """
        if hasattr(self, 'client'):
            self.client.sock.close()
        self.window.destroy()
        exit()
    
    def logout(self, alert=None):
        """
        Logs out of the current session/room
        Input:
            alert(optional)     alert that shows up on logout
        """
        if hasattr(self, 'client'):
            self.client.sock.close()
        self.window.geometry('360x360')
        self.switchFrame(LoginFrame)
        if alert:
            self.showWarning('A problem occured', alert)

    def checkNameChange(self, name):
        """
        Checks if user name assigned by the server differs from the one entered by them
        Input:
            name    name assigned by the server
        """
        if hasattr(self, 'enteredUsername'):
            if self.enteredUsername != name:
                self.showWarning('Name not available', f'The requested name {self.enteredUsername} was not available.\n {name} is your username instead.')

    def askQuestion(self, title, message):
        """
        Opens a question box with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        return messagebox.askquestion(title, message)

    def showError(self, title, message):
        """
        Opens an error box with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        messagebox.showerror(title, message)

    def showWarning(self, title, message):
        """
        Opens a warning box with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        messagebox.showwarning(title, message)

    def showInfo(self, title, message):
        """
        Opens an info box with specified title and message
        Input:
            title       popup title
            message     popup text
        """
        messagebox.showinfo(title, message)

class ApplicationFrame(Frame):
    """
    ApplicationFrame Class - responisble for the application view
    Attributes:
        gui          Tk class object, main window of the app
        users        list of users in the room
    Other attributes are Tkinter objects (Frame or otherwise), required for some GUI operations
    """
    def __init__(self, master, gui):
        """
        Initializes the frame with the reference to the gui:
        Input:
            master            the window with the frame
            gui               the reference to the GUI object
        """
        super().__init__(master)
        self.gui = gui
        self.users = []

        self.headerFrame = Frame(self)
        self.headerFrame.place(relwidth=1, relheight=0.05)
        self.makeHeader(self.headerFrame)

        self.textFrame = Frame(self)
        self.textFrame.place(rely=0.05, relwidth=1, relheight=0.5)
        self.makeTextArea(self.textFrame)

        self.inputFrame = Frame(self)
        self.inputFrame.place(rely=0.55, relwidth=0.5, relheight=0.15)
        self.makeInputArea(self.inputFrame)

        self.userListFrame = Frame(self)
        self.userListFrame.place(rely=0.55, relx=0.5, relwidth=0.5, relheight=0.35)
        self.makeUserList(self.userListFrame)

        self.exitFrame = Frame(self)
        self.exitFrame.place(rely=0.9, relwidth=1, relheight=0.1)
        self.makeExitArea(self.exitFrame)

    def sendChat(self, event):
        """
        Sends a chat message to the client via the GUI object
        Input: 
            event     event associated with the chat message being sent
        """
        chat = self.chatEntry.get().replace(MESSAGE_DELIMITER,'').replace(MESSAGE_END, '')
        if chat:
            self.gui.sendChat(chat)
            self.chatEntry.delete(0, END)
    
    def sendValue(self, override=None):
        """
        Sends a value to the client via the GUI object
        Input: 
            override    value used if the user does not input anything
        """
        if self.entryDone.get():
            return
        self.entryDone.set(True)
        self.valEntry.config(state=DISABLED)
        #Overriding value when the user does not input any value
        value = override or self.valEntry.get().replace(MESSAGE_DELIMITER,'').replace(MESSAGE_END, '')
        if value:
            randomness = self.gui.sendValue(value)
            if not override:
                self.valEntry.config(state=NORMAL)
                self.valEntry.delete(0, END)
                self.valEntry.config(state=DISABLED)
                self.valLabel.config(text='Your value has been submitted!')
            else:
                self.valLabel.config(text='A random value has been submitted!')

            self.rollDetails = {
                'value' : value,
                'override' : True if override else False,
                'randomness' : randomness
            }
            self.valButton.config(state=NORMAL)
            self.traceButton.config(state=NORMAL)

    def seeRollInfo(self):
        """
        Displays information about the roll in a messagebox
        """
        info = ''
        details = self.rollDetails
        if details:
            if details['override']:
                info += f'You failed to enter a value, so\n{details["value"]}\nwas chosen using system randomness.\n'
            else:
                info += f'Your input: {details["value"]}\n'
            info += f'It was used to calculate and submit your randomness, which is:\n{details["randomness"]}\n'
        if info:
            messagebox.showinfo('Roll summary', f'{info}')

    def seeTrace(self):
        """
        Displays calculation trace in a messagebox
        """
        trace = self.gui.getTrace()
        messagebox.showinfo('Your trace', trace)

    def addGmElements(self):
        """
        Adds GM-related functionality to the front-end
        """
        self.prepareCommandFrame()
        self.prepareSelectAllBtn()

    def prepareCommandFrame(self):
        """
        Prepares GUI Frame with GM commands
        """
        self.commandFrame = Frame(self)
        self.commandFrame.place(rely=0.7, relwidth=0.5, relheigh=0.2)
        self.makeCommandArea(self.commandFrame)

    def prepareSelectAllBtn(self):
        """
        Prepares a "Select All" button for the user list. GM-only functionality
        """
        self.selectAllBtn = Button(self.userListFrame, text='Select all', command=self.selectAll)
        self.selectAllBtn.place(relx=0.3, relwidth=0.4, rely=0.9, relheight=0.1)

    def startRoll(self):
        """
        Starts the roll, GM-only functionality
        """
        errors = ''
        timeout = self.timeoutSpinbox.get()
        errors += self.validateTimeout(timeout)
        maxNum = self.maxNumSpinbox.get()
        errors += self.validateMaxNum(maxNum)
        if errors:
            messagebox.showerror('Input validation failed', f'Your input contains the following errors:\n{errors}')
        else:
            selection = list(self.userList.curselection()) 
            if 0 not in selection:
                selection.append(0)
            selectedUsers = [self.userList.get(idx).strip() for idx in selection]
            selectedUsers[0] = selectedUsers[0].rstrip('(GM)').strip()
            self.gui.startRoll(timeout, maxNum, selectedUsers)

    def getUserValue(self):
        """
        Prompts the user to enter a value and waits for them to do it
        """
        self.entryDone.set(False)
        self.valEntry.config(state=NORMAL)
        self.valLabel.config(text='Enter your randomness')
        self.wait_variable(self.entryDone)

    def getUsers(self):
        """
        A getter for users in the room
        Output:
            a list of users
        """
        return self.users

    def updateUserList(self):
        """
        Updates the user list with latest data
        """
        self.userList.delete(0, END)
        for user in self.users:
            self.userList.insert(END, f'{user}\n')
    
    def setUserList(self, users):
        """
        A setter for user lists:
        Input:
            users       new list of users
        """
        self.users = users
        self.updateUserList()

    def print(self, message):
        """
        Prints messages to appropriate textfield
        Input:
            message     message to be printed
        """
        self.text.config(state=NORMAL)
        self.text.insert(END, message if message.endswith('\n') else f'{message}\n')
        self.text.config(state=DISABLED)
        self.text.yview_pickplace('end') 

    def makeHeader(self, master):
        """
        Prepares the header Label
        """
        self.header = Label(master, font=('Helvetica', 16))
        self.header.pack()

    def setHeader(self, text):
        """
        Changes the header text
        Input:
            text        new header text
        """
        self.header.config(text=text)

    def selectAll(self):
        """
        Selects all of the users from the list
        """
        self.userList.select_set(0,END)

    def validateTimeout(self, timeout):
        """
        Validate user-entered timeout
        Input:
            timeout
        Output:
            error message or empty string
        """
        msg = ''
        if not timeout.isnumeric():
            msg += f'Timeout should be a number\n'
        elif int(timeout) not in range(2,300):
            msg += f'Timeout should not be smaller than 2 seconds and should not exceed 300 seconds\n'
        return msg

    def validateMaxNum(self, maxNum):
        """
        Validate user-entered maxNum
        Input:
            maxNum
        Output:
            error message or empty string
        """
        msg = ''
        if not maxNum.isnumeric():
            msg += f'Max number has to be a number\n'
        elif int(maxNum) < 2:
            msg += f'Max number cannot be smaller than 2\n'
        return msg

    def makeTextArea(self, master):
        """
        Fills the textFrame with contents
        Input:
            master      textFrame in the ApplicationFrame
        """
        self.text = Text(master)
        self.scrollbar = Scrollbar(master)
        self.text.place(relwidth=0.95, relheight=0.95)
        self.scrollbar.place(relx=0.95, relwidth=0.05, relheight=1)
        self.text.config(yscrollcommand=self.scrollbar.set, state=DISABLED)
        self.scrollbar.config(command=self.text.yview)

        self.chatEntry = Entry(master)
        self.chatEntry.place(relwidth=0.95, rely=0.95, relheight=0.05)
        self.chatEntry.bind('<Return>', self.sendChat)

    def makeInputArea(self, master):
        """
        Fills the inputFrame with contents
        Input:
            master      inputFrame in the ApplicationFrame
        """
        self.valEntry = Entry(master, state=DISABLED)
        self.valEntry.bind('<Return>', lambda event: self.sendValue())

        self.valLabel = Label(master)

        self.entryDone = BooleanVar(False)

        self.valButton = Button(master, text='Roll info', command=self.seeRollInfo, state=DISABLED)
        self.traceButton = Button(master, text='Trace', command=self.seeTrace, state=DISABLED)

        self.valEntry.place(relx=0.15, relwidth=0.7, rely = 0.1, relheight=0.2)
        self.valLabel.place(relx=0.05, relwidth=0.9, rely = 0.4, relheight=0.2)
        self.valButton.place(relx=0.15, relwidth=0.3, rely = 0.7, relheight=0.2)
        self.traceButton.place(relx=0.55, relwidth=0.3, rely = 0.7, relheight=0.2)

    def makeCommandArea(self, master):
        """
        Fills the commandFrame with contents
        Input:
            master      commandFrame in the ApplicationFrame
        """
        self.timeoutLabel = Label(master, text='Timeout', anchor='e')
        self.timeoutSpinbox = Spinbox(master, from_ = 2, to = 300)

        self.maxNumLabel = Label(master, text='Max', anchor='e')
        self.maxNumSpinbox = Spinbox(master, from_ = 2, to=10000)
        
        self.rollButton = Button(master, text='Roll', command=self.startRoll)

        self.timeoutLabel.place(rely=0.1, relx=0.1, relwidth=0.3, relheight=0.2)
        self.timeoutSpinbox.place(rely=0.1, relx=0.5, relwidth=0.3, relheight=0.2)
        self.maxNumLabel.place(rely=0.4, relx=0.1, relwidth=0.3, relheight=0.2)
        self.maxNumSpinbox.place(rely=0.4, relx=0.5, relwidth=0.3, relheight=0.2)
        self.rollButton.place(rely=0.7, relx=0.2, relwidth=0.6, relheight=0.2)

    def makeUserList(self, master):
        """
        Fills the userListFrame with contents
        Input:
            master      userListFrame in the ApplicationFrame
        """
        self.userList = Listbox(master, selectmode=MULTIPLE, activestyle='none')
        self.userListScrollbar = Scrollbar(master)

        self.userList.place(relwidth=0.95, relheight=0.9)
        self.userListScrollbar.place(relx=0.95, relwidth=0.05, relheight=0.9)
        
        self.userList.config(yscrollcommand=self.userListScrollbar.set, state=NORMAL)
        self.userListScrollbar.config(command=self.userList.yview)

    def makeExitArea(self, master):
        """
        Fills the exitFrame with contents
        Input:
            master      exitFrame in the ApplicationFrame
        """
        self.exitBtn = Button(master, text='Logout', command=self.gui.logout)
        self.exitBtn.place(relx=0.3, relwidth=0.4, rely=0.6)

class LoginFrame(Frame):
    """
    LoginFrame Class - responisble for the login view
    Attributes:
        gui          Tk class object, main window of the app
    Other attributes are Tkinter objects, mostly Labels and Entries.
    """
    def __init__(self, master, gui, host=None, port=None, username=None, room=None):
        """
        Initializes LoginFrame
        Input:
            master              the window with the frame
            gui                 the reference to the GUI object
            host (optional)     for pre-filling user input field
            port (optional)     for pre-filling user input field
            username (optional) for pre-filling user input field
            room (optional)     for pre-filling user input field
        """
        super().__init__(master)
        self.gui = gui

        self.labelHost = Label(self, text='Host', font=('Helvetica', 14), anchor='e')
        self.labelPort = Label(self, text='Port', font=('Helvetica', 14), anchor='e')
        self.labelUsername = Label(self, text='Username', font=('Helvetica', 14), anchor='e')
        self.labelRoom = Label(self, text='Room', font=('Helvetica', 14), anchor='e')

        self.entryHost = Entry(self, font=('Helvetica', 14))
        self.entryPort = Entry(self, font=('Helvetica', 14))
        self.entryUsername = Entry(self, font=('Helvetica', 14))
        self.entryRoom = Entry(self, font=('Helvetica', 14))

        self.labelHost.place(rely=0.1, relwidth=0.35, relheight=0.1)
        self.labelPort.place(rely=0.25, relwidth=0.35, relheight=0.1)
        self.labelUsername.place(rely=0.4, relwidth=0.35, relheight=0.1)
        self.labelRoom.place(rely=0.55, relwidth=0.35, relheight=0.1)

        self.entryHost.place(rely=0.1, relx=0.36, relwidth=0.5, relheight=0.1)
        self.entryPort.place(rely=0.25, relx=0.36, relwidth=0.5, relheight=0.1)
        self.entryUsername.place(rely=0.4, relx=0.36, relwidth=0.5, relheight=0.1)
        self.entryRoom.place(rely=0.55, relx=0.36, relwidth=0.5, relheight=0.1)

        self.assignRoom = BooleanVar(False)
        self.checkbutton = Checkbutton(self, text="Assign me to a new room", command=self.toggleRoomEntry, var=self.assignRoom)
        self.checkbutton.place(rely=0.65, relx=0.25, relwidth=0.5, relheight=0.1)

        self.button = Button(self, text='Login', command=self.loginButtonClicked, font=('Helvetica', 16), anchor='center')
        self.button.place(rely=0.75, relx=0.3, relwidth=0.4, relheight=0.1)
        
        if hasattr(self.gui, 'host'):
            self.entryHost.insert(0, self.gui.host)
        if hasattr(self.gui, 'port'):
            self.entryPort.insert(0, self.gui.port)
        if hasattr(self.gui, 'username'):
            self.entryUsername.insert(0, self.gui.username)
        if hasattr(self.gui, 'room'):
            self.entryRoom.insert(0, self.gui.room)

    def loginButtonClicked(self):
        """
        Triggered when "Login" button is clicked. Validates data and attempts login.
        """
        errors = ''
        host = self.entryHost.get()
        errors += self.validateHost(host)
        port = self.entryPort.get()
        errors += self.validatePort(port)
        username = self.entryUsername.get()
        errors += self.validateUsername(username)
        if self.assignRoom.get():
            room = None
        else:
            room = self.entryRoom.get()
            errors += self.validateRoom(room)
        if errors:
            messagebox.showerror('Input validation failed', f'Your input contains the following errors:\n{errors}')
        else:
            self.gui.launchClient(host,port,username,room)

    def toggleRoomEntry(self):
        """
        Triggered when "Assign me a new room" is toggled.
        """
        if self.assignRoom.get():
            self.entryRoom.config(state=DISABLED)
        else:
            self.entryRoom.config(state=NORMAL)

    def validateHost(self, host):
        """
        Validate user-entered hostname
        Input:
            hostname
        Output:
            error message or empty string
        """
        msg = ''
        return msg
    
    def validatePort(self, port):
        """
        Validate user-entered port
        Input:
            port
        Output:
            error message or empty string
        """
        msg = ''
        if not port.isnumeric():
            msg += f'Port should be a number\n'
        elif int(port) not in range(0,65536):
            msg += f'Port should be in range 0-65535\n'
        return msg

    def validateUsername(self, username):
        """
        Validate user-entered username
        Input:
            username
        Output:
            error message or empty string
        """
        msg = ''
        self.gui.enteredUsername = username
        if len(username) not in range(MIN_USERNAME_CHARS, MAX_USERNAME_CHARS+1):
            msg += f'Username must be between {MIN_USERNAME_CHARS} and {MAX_USERNAME_CHARS} long\n'
        if not username.isalnum():
            msg += f'Username must not contain non-alphanumeric characters\n'
        return msg

    def validateRoom(self, room):
        """
        Validate user-entered room number
        Input:
            room
        Output:
            error message or empty string
        """
        msg = ''
        if len(room) not in range(MIN_ROOM_NUMBER_CHARS, MAX_ROOM_NUMBER_CHARS+1):
             msg += f'Room ID must be between {MIN_ROOM_NUMBER_CHARS} and {MAX_ROOM_NUMBER_CHARS} long\n'
        return msg

if __name__ == '__main__':
    GUI()

