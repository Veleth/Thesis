from tkinter import *
from tkinter import messagebox
from client import Client
import threading
#TODO: remove
from communication import *
#temporary
import hashlib
import time
import random
# https://stackoverflow.com/questions/4770993/how-can-i-make-silent-exceptions-louder-in-tkinter
# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# http://effbot.org/tkinterbook/button.htm
class GUI():
    def __init__(self):
        self.window = Tk()
        self.window.title('Login screen')
        self.window.resizable(False,False)
        self.window.protocol('WM_DELETE_WINDOW', self.exit)
        canvas = Canvas(self.window, height=360, width=360)
        canvas.pack()
        
        self._frame = None
        self.switch_frame(LoginFrame)
        self.launchClient(host=IPADDR, port=8000, username=str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]) , room='22')#TODO: Remove
        self.window.mainloop()

    def launchClient(self, host, port, username, room):
        try:
            self.client = Client(host, int(port), username, room, gui=self)
            self.switch_frame(ApplicationFrame)
            self.window.geometry('480x720')
        except:
            self.host = host
            self.port = port
            self.username = username
            self.room = room
            messagebox.showerror('Connection error', f'Host {host} is not responding on port {port}\nMake sure the information is correct and the server is properly configured')
            self.switch_frame(LoginFrame)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self.window, self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def print(self, message):
        #Todo: check if application frame
        self._frame.print(message)

    def sendChat(self, message):
        self.client.sendChat(message)
    
    def sendValue(self, value):
        return self.client.sendValue(value)

    def refreshHeader(self):
        #TODO: check if application frame
        self._frame.setHeader(self.getHeader())

    def getHeader(self):
        return f'{self.client.username} (GM) - Room {self.client.room}' if self.client.isGM else f'{self.client.username} - Room {self.client.room}'

    def isGM(self):
        return self.client.isGM

    def getUserValue(self, timeout, maxNum):
        #TODO: do something with maxNum
        #check frame
        thread = threading.Thread(target=self._frame.getUserValue, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        if self._frame.entryDone.get():
            pass
        else:
            self._frame.sendValue(self.client.getRandomValue())

    def setUserList(self, users):
        #TODO: check if application frame
        self._frame.setUserList(users)

    def startRoll(self, timeout, maxNum):
        self.client.startRoll(timeout, maxNum)

    def exit(self):
        if hasattr(self, 'client'):
            self.client.sock.close()
        self.window.destroy()
        exit()

class ApplicationFrame(Frame):
    def __init__(self, master, gui):
        super().__init__(master, bg='#ABABAB')
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

        self.commandFrame = Frame(self)
        self.commandFrame.place(rely=0.7, relwidth=0.5, relheigh=0.2)
        self.makeCommandArea(self.commandFrame)

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
        self.entryDone.set(True)
        self.valEntry.config(state=DISABLED)
        value = override or self.valEntry.get().replace(MESSAGE_DELIMITER,'').replace(MESSAGE_END, '')
        if value:
            randomness = self.gui.sendValue(value)
            self.valEntry.delete(0, END)
            #TODO: prompt or something

    def startRoll(self, timeout, maxNum):
        self.gui.startRoll(timeout, maxNum)

    def getUserValue(self):
        self.entryDone.set(False)
        self.valEntry.config(state=NORMAL)
        self.valLabel.config(text='Enter your randomness')
        self.wait_variable(self.entryDone)

    def getUsers(self):
        return self.users

    def updateUserList(self):
        self.userList.config(state=NORMAL)
        self.userList.delete(1.0, END)
        for user in self.users:
            self.userList.insert(END, f'{user}\n')
        self.userList.delete('end-1c', 'end')
        self.userList.config(state=DISABLED)
    
    def setUserList(self, users):
        self.users = users
        self.updateUserList()

    def print(self, message):
        self.text.config(state=NORMAL)
        self.text.insert(END, message if message.endswith('\n') else f'{message}\n')
        self.text.config(state=DISABLED)
        self.text.yview_pickplace('end') 

    def makeHeader(self, master):
        self.header = Label(master, text=self.gui.getHeader(), font=('Helvetica', 16))
        self.header.pack()

    def setHeader(self, text):
        self.header.config(text=text)

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
        #TODO: Work on placement and label
        self.valEntry = Entry(master, state=DISABLED)
        self.valEntry.pack()
        self.valEntry.bind('<Return>', self.sendValue)

        self.valLabel = Label(master, text='placeholder')
        self.valLabel.pack()
        self.entryDone = BooleanVar(False)

    def makeCommandArea(self, master):
        #TODO: Validate GM role
        self.timeoutLabel = Label(master, text='Timeout', anchor='e')
        self.timeoutSpinbox = Spinbox(master, from_ = 1, to = 300)

        self.maxLabel = Label(master, text='Max', anchor='e')
        self.maxEntry = Entry(master)
        
        self.rollButton = Button(master, text='Roll', command=self.startRoll)

        self.timeoutLabel.place(rely=0.1, relx=0, relwidth=0.3, relheight=0.2)
        self.timeoutSpinbox.place(rely=0.1, relx=0.5, relwidth=0.4, relheight=0.2)
        self.maxLabel.place(rely=0.4, relx=0.2, relwidth=0.5, relheight=0.2)
        self.maxEntry.place(rely=0.4, relx=0.2, relwidth=0.5, relheight=0.2)
        self.rollButton.place(rely=0.7, relx=0.2, relwidth=0.7, relheight=0.2)

    def makeUserList(self, master):
        self.userList = Text(master)
        self.userListScrollbar = Scrollbar(master)
        self.userList.place(relwidth=0.95, relheight=1)
        self.userListScrollbar.place(relx=0.95, relwidth=0.05, relheight=1)
        self.userList.config(yscrollcommand=self.userListScrollbar.set, state=DISABLED)
        self.userListScrollbar.config(command=self.userList.yview)

    def makeExitArea(self, master):
        self.exitBtn = Button(master, text='Exit/Logout', command=self.gui.exit)
        self.exitBtn.pack()

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

        self.button = Button(self, text='Login', command=self.loginButtonClicked, font=('Helvetica', 16), anchor='center')
        self.button.place(rely=0.7, relx=0.3, relwidth=0.4, relheight=0.1)

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
        room = self.entryRoom.get()
        errors += self.validateRoom(room)
        if errors:
            messagebox.showerror('Input validation failed', f'Your input contains the following errors:\n{errors}')
        else:
            self.gui.launchClient(host,port,username,room)

    def validateHost(self, host):
        msg = ''
        #TODO: come up with hostname validation
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
        #TODO: Move to config?
        minChars = 1
        maxChars = 32
        if len(username) not in range(minChars, maxChars+1):
            msg += f'Username must be between {minChars} and {maxChars} long\n'
        if not username.isalnum():
            msg += f'Username must not contain non-alphanumeric characters\n'
        return msg

    def validateRoom(self, room):
        msg = ''
        #TODO: Move to config?
        minChars = 1
        maxChars = 20
        if len(room) not in range(minChars, maxChars+1):
             msg += f'Room ID must be between {minChars} and {maxChars} long\n'
        return msg

if __name__ == '__main__':
    GUI()