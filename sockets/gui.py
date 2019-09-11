from tkinter import *
from client import Client

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

        canvas = Canvas(self.window, height=360, width=360)
        canvas.pack() 
        
        self._frame = None
        self.switch_frame(LoginFrame)

        self.window.mainloop()

    def launchClient(self, host, port, username, room):
        self.switch_frame(ApplicationFrame)
        self.window.geometry('480x720')
        # self.client = Client(host, int(port), username, room, gui=self)
        # #TODO: Something went wrong OR Welcome to the server
        # self.changeView()

    def switch_frame(self, frame_class):
        new_frame = frame_class(self.window, self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

class LoginFrame(Frame):
    def __init__(self, master, gui):
        super().__init__(master, bg='#0FACD0')
        self.gui = gui

        self.label_host = Label(self, text="Host", font=('Helvetica', 16))
        self.label_port = Label(self, text="Port")
        self.label_username = Label(self, text="Username")
        self.label_room = Label(self, text="Room")

        self.entry_host = Entry(self)
        self.entry_port = Entry(self)
        self.entry_username = Entry(self)
        self.entry_room = Entry(self)
        self.label_host.grid(row=0, sticky=E)
        self.label_port.grid(row=1, sticky=E)
        self.label_username.grid(row=2, sticky=E)
        self.label_room.grid(row=3, sticky=E)

        self.entry_host.grid(row=0, column=1)
        self.entry_port.grid(row=1, column=1)
        self.entry_username.grid(row=2, column=1)
        self.entry_room.grid(row=3, column=1)

        self.button = Button(self, text='Go!', command=self.login_btn_clicked)
        self.button.grid(columnspan=2)

        #Later remove
        self.entry_host.insert(0, '127.0.0.1')
        self.entry_port.insert(0, '8000')
        self.entry_username.insert(0, str(hashlib.sha256(str(time.time()+random.random()).encode()).hexdigest()[:5]))
        self.entry_room.insert(0, '22')

    def login_btn_clicked(self):
        #TODO: Validate data
        host = self.entry_host.get()
        port = self.entry_port.get()
        username = self.entry_username.get()
        room = self.entry_room.get()
        self.gui.launchClient(host,port,username,room)

class ApplicationFrame(Frame):
    def __init__(self, master, gui):
        super().__init__(master, bg='#ABABAB')
        self.gui = gui

        #     #self initialform
    #     messages_frame = Frame(self.window)
    #     message = StringVar()
    #     message.set('Typee here')
    #     scrollbar = Scrollbar(messages_frame)

    #     msg_list = Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    #     scrollbar.pack(side=RIGHT, fill=Y)
    #     msg_list.pack(side=LEFT, fill=BOTH)
    #     msg_list.pack()

    #     entry_field = Entry(self.window, textvariable=message)
    #     entry_field.bind("<Return>", self.send)
    #     entry_field.pack()
    #     send_button = Button(self.window, text="Send", command=self.send)
    #     send_button.pack()

    #     messages_frame.pack()
    #     label = Label(self.window, text="ez")
    #     label.pack()
    #     self.window.mainloop()
        

    # def send(self, event=None):  # event is passed by binders.
    #     """Handles sending of messages."""
    #     msg = message.get()
    #     message.set("")  # Clears input field.
    #     print(msg)
    #     # if msg == "{quit}":
    #     #     client_socket.close()
    #     #     top.quit()

if __name__ == '__main__':
    GUI()