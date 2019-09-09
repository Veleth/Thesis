from tkinter import *


# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# http://effbot.org/tkinterbook/button.htm
class GUI():
    def __init__(self):
        self.window = Tk()
        self.window.title('Client')
        lf = LoginFrame(self.window)
        self.window.mainloop()
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

class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.label_host = Label(self, text="Host")
        self.label_port = Label(self, text="Port")
        self.label_username = Label(self, text="Username")
        self.label_room = Label(self, text="Room")

        global lll 
        lll = 123

        self.entry_username = Entry(self)
        self.entry_password = Entry(self, show="*")

        self.label_username.grid(row=0, sticky=E)
        self.label_password.grid(row=1, sticky=E)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        self.checkbox = Checkbutton(self, text="Keep me logged in")
        self.checkbox.grid(columnspan=2)

        self.logbtn = Button(self, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)

        self.pack()

    def _login_btn_clicked(self):
        # print("Clicked")
        username = self.entry_username.get()
        password = self.entry_password.get()

        # print(username, password)

        if username == "john" and password == "password":
            tm.showinfo("Login info", "Welcome John")
        else:
            tm.showerror("Login error", "Incorrect username")
GUI()