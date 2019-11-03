from tkinter import *
from tkinter import messagebox
from client import Client
import threading, logging
from communication import *
#temporary
from config import IPADDR, MIN_USERNAME_CHARS, MAX_USERNAME_CHARS, MIN_ROOM_NUMBER_CHARS, MAX_ROOM_NUMBER_CHARS
import hashlib
import time
import random
# https://stackoverflow.com/questions/4770993/how-can-i-make-silent-exceptions-louder-in-tkinter
class GUI():
    def __init__(self):
        self.window = Tk()
        self.window.title('Login screen')
        self.window.resizable(False,False)
        self.window.protocol('WM_DELETE_WINDOW', self.exit)
        canvas = Canvas(self.window, height=360, width=360)
        canvas.pack()
        
        self._frame = None
        self.switchFrame(LoginFrame)
        self.launchClient(host=IPADDR, port=8000, username=str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]) , room='22')#TODO: Remove
        self.window.mainloop()

    def launchClient(self, host, port, username, room):
        try:
            self.switchFrame(ApplicationFrame)
            self.window.geometry('480x720')
            self.client = Client(host, int(port), username, room, gui=self)
        except:
            logging.exception('someerror')#TODO: remove
            self.window.geometry('360x360')
            self.host = host
            self.port = port
            self.username = username
            self.room = room
            messagebox.showerror('Connection error', f'Host {host} is not responding on port {port}\nMake sure the information is correct and the server is properly configured')
            self.switchFrame(LoginFrame)

    def switchFrame(self, frame_class):
        new_frame = frame_class(self.window, self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def print(self, message):
        #Todo: check if application frame
        self._frame.print(message)

    def sendChat(self, message):
        #TODO config:
        maxLength = 140
        self.client.sendChat(message[:maxLength])
    
    def sendValue(self, value):
        return self.client.sendValue(value)

    def refreshHeader(self):
        #TODO: check if application frame
        self._frame.setHeader(self.getHeader())

    def getHeader(self):
        return f'{self.client.username} (GM) - Room {self.client.room}' if self.client.isGM else f'{self.client.username} - Room {self.client.room}'

    def isGM(self):
        return self.client.isGM

    def getTrace(self):
        if self.client.ownResult:
            return f'Roll start: {self.client.rollTime}\nYour value: {self.client.ownValue}\n{self.client.ownTrace}'
        else:
            return f'No calculations have taken place yet.\nWait for others to submit their values.'
    
    def getUserValue(self, timeout, maxNum):
        #TODO: do something with maxNum
        #TODO: check frame
        thread = threading.Thread(target=self._frame.getUserValue, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        if self._frame.entryDone.get():
            pass
        else:
            self._frame.sendValue(self.client.getRandomValue())

    def addGmElements(self):
        #TODO: check if application frame
        self._frame.addGmElements() 

    def setUserList(self, users):
        #TODO: check if application frame
        self._frame.setUserList(users)

    def startRoll(self, timeout, maxNum, participants):
        self.client.startRoll(timeout, maxNum, participants)

    def exit(self):
        if hasattr(self, 'client'):
            self.client.sock.close()
        self.window.destroy()
        exit()
    
    def logout(self, alert=None):
        if hasattr(self, 'client'):
            self.client.sock.close()
        self.window.geometry('360x360')
        self.switchFrame(LoginFrame)
        if alert:
            self.showwarning('A problem occured', alert)

    def checkNameChange(self, name):
        if hasattr(self, 'enteredUsername'):
            if self.enteredUsername != name:
                self.showwarning('Name not available', f'The requested name {self.enteredUsername} was not available.\n {name} is your username instead.')

    def askQuestion(self, title, message):
        return messagebox.askquestion(title, message)

    def showError(self, title, message):
        messagebox.showerror(title, message)

    def showWarning(self, title, message):
        messagebox.showwarning(title, message)

    def showInfo(self, title, message):
        messagebox.showinfo(title, message)

class ApplicationFrame(Frame):
    def __init__(self, master, gui):
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
        chat = self.chatEntry.get().replace(MESSAGE_DELIMITER,'').replace(MESSAGE_END, '')
        if chat:
            self.gui.sendChat(chat)
            self.chatEntry.delete(0, END)
    
    def sendValue(self, override=None):
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
        trace = self.gui.getTrace()
        messagebox.showinfo('Your trace', trace)

    def addGmElements(self):
        self.prepareCommandFrame()
        self.prepareSelectAllBtn()

    def prepareCommandFrame(self):
        self.commandFrame = Frame(self)
        self.commandFrame.place(rely=0.7, relwidth=0.5, relheigh=0.2)
        self.makeCommandArea(self.commandFrame)

    def prepareSelectAllBtn(self):
        self.selectAllBtn = Button(self.userListFrame, text='Select all', command=self.selectAll)
        self.selectAllBtn.place(relx=0.3, relwidth=0.4, rely=0.9, relheight=0.1)

    def startRoll(self):
        #TODO: Data validation and prompt
        errors = ''
        timeout = self.timeoutSpinbox.get()
        errors += self.validateTimeout(timeout)
        maxNum = self.maxNumSpinbox.get()
        errors += self.validateMaxNum(maxNum)
        if errors:
            pass #TODO
        else:
            selection = list(self.userList.curselection()) 
            selectedUsers = [self.userList.get(idx).strip() for idx in [selection if 0 in selection else [0] + selection]]
            selectedUsers[0] = selectedUsers[0].rstrip('(GM)').strip()
            self.gui.startRoll(timeout, maxNum, selectedUsers)

    def getUserValue(self):
        self.entryDone.set(False)
        self.valEntry.config(state=NORMAL)
        self.valLabel.config(text='Enter your randomness')
        self.wait_variable(self.entryDone)

    def getUsers(self):
        return self.users

    def updateUserList(self):
        self.userList.delete(0, END)
        for user in self.users:
            self.userList.insert(END, f'{user}\n')
    
    def setUserList(self, users):
        self.users = users
        self.updateUserList()

    def print(self, message):
        self.text.config(state=NORMAL)
        self.text.insert(END, message if message.endswith('\n') else f'{message}\n')
        self.text.config(state=DISABLED)
        self.text.yview_pickplace('end') 

    def makeHeader(self, master):
        self.header = Label(master, font=('Helvetica', 16))
        self.header.pack()

    def setHeader(self, text):
        self.header.config(text=text)

    def selectAll(self):
        self.userList.select_set(0,END)

    def validateTimeout(self, timeout):
        pass #TODO: implement

    def validateMaxNum(self, maxNum):
        pass #TODO: implement

    def makeTextArea(self, master):
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
        self.timeoutLabel = Label(master, text='Timeout', anchor='e')
        self.timeoutSpinbox = Spinbox(master, from_ = 1, to = 300)

        self.maxNumLabel = Label(master, text='Max', anchor='e')
        self.maxNumSpinbox = Spinbox(master, from_ = 2, to=10000)
        
        self.rollButton = Button(master, text='Roll', command=self.startRoll)

        self.timeoutLabel.place(rely=0.1, relx=0.1, relwidth=0.3, relheight=0.2)
        self.timeoutSpinbox.place(rely=0.1, relx=0.5, relwidth=0.3, relheight=0.2)
        self.maxNumLabel.place(rely=0.4, relx=0.1, relwidth=0.3, relheight=0.2)
        self.maxNumSpinbox.place(rely=0.4, relx=0.5, relwidth=0.3, relheight=0.2)
        self.rollButton.place(rely=0.7, relx=0.2, relwidth=0.6, relheight=0.2)

    def makeUserList(self, master):
        self.userList = Listbox(master, selectmode=MULTIPLE, activestyle='none')
        self.userListScrollbar = Scrollbar(master)

        self.userList.place(relwidth=0.95, relheight=0.9)
        self.userListScrollbar.place(relx=0.95, relwidth=0.05, relheight=0.9)
        
        self.userList.config(yscrollcommand=self.userListScrollbar.set, state=NORMAL)
        self.userListScrollbar.config(command=self.userList.yview)

    def makeExitArea(self, master):
        self.exitBtn = Button(master, text='Logout', command=self.gui.logout)
        self.exitBtn.place(relx=0.3, relwidth=0.4, rely=0.6)

class LoginFrame(Frame):
    def __init__(self, master, gui, host=None, port=None, username=None, room=None):
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
        
        #TODO: Later switch
        # if self.gui.host:
        #     self.entryHost.insert(0, self.gui.host)
        # if self.gui.port:
        #     self.entryPort.insert(0, self.gui.port)
        # if self.gui.username:
        #     self.entryUsername.insert(0, self.gui.username)
        # if self.gui.room:
        #     self.entryRoom.insert(0, self.gui.room)

        self.entryHost.insert(0, IPADDR)
        self.entryPort.insert(0, '8000')
        self.entryUsername.insert(0, str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]))
        self.entryRoom.insert(0, '22')

    def loginButtonClicked(self):
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
        if self.assignRoom.get():
            self.entryRoom.config(state=DISABLED)
        else:
            self.entryRoom.config(state=NORMAL)

    def validateHost(self, host):
        msg = ''
        return msg
    
    def validatePort(self, port):
        msg = ''
        if not port.isnumeric():
            msg += f'Port should be a number'
        elif int(port) not in range(0,65536):
            msg += f'Port should be in range 0-65535'
        return msg

    def validateUsername(self, username):
        msg = ''
        self.gui.enteredUsername = username
        if len(username) not in range(MIN_USERNAME_CHARS, MAX_USERNAME_CHARS+1):
            msg += f'Username must be between {MIN_USERNAME_CHARS} and {MAX_USERNAME_CHARS} long\n'
        if not username.isalnum():
            msg += f'Username must not contain non-alphanumeric characters\n'
        return msg

    def validateRoom(self, room):
        msg = ''
        if len(room) not in range(MIN_ROOM_NUMBER_CHARS, MAX_ROOM_NUMBER_CHARS+1):
             msg += f'Room ID must be between {MIN_ROOM_NUMBER_CHARS} and {MAX_ROOM_NUMBER_CHARS} long\n'
        return msg

if __name__ == '__main__':
    GUI()

