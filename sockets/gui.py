from tkinter import *
from client import Client
import threading
#TODO: remove
from communication import *
#temporary
import hashlib
import time
import random

# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# http://effbot.org/tkinterbook/button.htm
class GUI():
    def __init__(self):
        self.window = Tk()
        self.window.title('Login screen')
        self.window.resizable(False,False)
        self.window.protocol("WM_DELETE_WINDOW", self.exit)
        canvas = Canvas(self.window, height=360, width=360)
        canvas.pack() 
        
        self._frame = None
        # self.switch_frame(LoginFrame)
        self.launchClient(host=IPADDR, port=8000, username=str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]) , room='22')#TODO: Remove
        self.window.mainloop()

    def launchClient(self, host, port, username, room):
        self.client = Client(host, int(port), username, room, gui=self)
        # #TODO: Something went wrong OR Welcome to the server
        self.switch_frame(ApplicationFrame)
        self.window.geometry('480x720')

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

    def getHeader(self):
        return f'{self.client.username} (GM) - Room {self.client.room}' if self.client.isGM else f'{self.client.username} - Room {self.client.room}'

    def isGM(self):
        return self.client.isGM

    def getUserValue(self, timeout, max):
        #TODO: do something with max
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

    def exit(self):
        #remove client too
        self.client.sock.close()
        self.window.destroy()
        exit()
        pass

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
        self.inputFrame.place(rely=0.75, relwidth=1, relheight=0.1)
        self.makeInputArea(self.inputFrame)

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

    def getUserValue(self):
        self.entryDone.set(False)
        self.valEntry.config(state=NORMAL)
        self.valLabel.config(text='Enter your randomness')
        self.wait_variable(self.entryDone)

    def getUsers(self):
        return self.users

    def updateUserList(self):
        pass #TODO: add functionality

    def setUserList(self, users):
        self.users = users
        self.updateUserList()

    def print(self, message):
        self.text.config(state=NORMAL)
        self.text.insert(END, message if message.endswith('\n') else f'{message}\n')
        self.text.config(state=DISABLED)

    def makeHeader(self, master):
        self.header = Label(master, text=self.gui.getHeader(), font=('Helvetica', 16))
        self.header.pack()

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
        self.valEntry.pack()
        self.valEntry.bind('<Return>', self.sendValue)

        self.valLabel = Label(master, text='ABC')
        self.valLabel.pack()
        self.entryDone = BooleanVar(False)

    def makeExitArea(self, master):
        self.exitBtn = Button(master, text='Exit/Logout', command=self.gui.exit)
        self.exitBtn.pack()


    # def makeUserList(self, master):

class LoginFrame(Frame):
    def __init__(self, master, gui):
        super().__init__(master, bg='#0FACD0')
        self.gui = gui

        self.labelHost = Label(self, text="Host", font=('Helvetica', 16))
        self.labelPort = Label(self, text="Port")
        self.labelUsername = Label(self, text="Username")
        self.labelRoom = Label(self, text="Room")

        self.entryHost = Entry(self)
        self.entryPort = Entry(self)
        self.entryUsername = Entry(self)
        self.entryRoom = Entry(self)
        self.labelHost.grid(row=0, sticky=E)
        self.labelPort.grid(row=1, sticky=E)
        self.labelUsername.grid(row=2, sticky=E)
        self.labelRoom.grid(row=3, sticky=E)

        self.entryHost.grid(row=0, column=1)
        self.entryPort.grid(row=1, column=1)
        self.entryUsername.grid(row=2, column=1)
        self.entryRoom.grid(row=3, column=1)

        self.button = Button(self, text='Go!', command=self.loginButtonClicked)
        self.button.grid(columnspan=2)

        #TODO: Later remove
        self.entryHost.insert(0, IPADDR)
        self.entryPort.insert(0, '8000')
        self.entryUsername.insert(0, str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]))
        self.entryRoom.insert(0, '22')

    def loginButtonClicked(self):
        #TODO: Validate data
        host = self.entryHost.get()
        port = self.entryPort.get()
        username = self.entryUsername.get()
        room = self.entryRoom.get()
        self.gui.launchClient(host,port,username,room)

if __name__ == '__main__':
    GUI()