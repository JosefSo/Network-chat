import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from PIL import ImageTk, Image

from Client import Client


class GUI:
    def __init__(self):
        msg = tkinter.Tk()
        msg.withdraw()

        self.name = simpledialog.askstring("Username", "Please choose your username", parent=msg)
        if self.name is None or self.name == "":
            return
        # no space in username
        if ' ' in self.name:
            n = ''
            for i in self.name:
                if i == ' ':
                    n += '_'
                else:
                    n += i
            self.name = n
        self.c = Client(self.name)
        self.done = False
        self.gui_thread = threading.Thread(target=self.gui)
        self.receive_thread = threading.Thread(target=self.resive)

        self.gui_thread.start()
        self.receive_thread.start()

    def gui(self):
        self.win = tkinter.Tk()
        # my_img = ImageTk.PhotoImage(Image.open("images.png"))
        # my_label = tkinter.Label(self.win, image=my_img)
        # my_label.pack()
        self.win.configure(bg="lightgray")
        self.chat_l = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_l.config(font=("Arial", 12))
        self.chat_l.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_l = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_l.config(font=("Arial", 12))
        self.msg_l.pack(padx=20, pady=5)

        self.input = tkinter.Text(self.win, height=3)
        self.input.pack(padx=20, pady=5)
        # Send Button
        self.s_button = tkinter.Button(self.win, text="Send", command=self.text)
        self.s_button.config(font=("Arial", 12))
        self.s_button.pack(padx=20, pady=5)
        self.win.protocol("VM_DELETE_WINDOW", self.disconnect)
        self.done = True
        self.win.mainloop()
        # if len(self.c.msglist) > 1:
        #     self.resive(self.c.massage_in)

    def text(self):
        msg = self.input.get('1.0', 'end')
        # print(msg)
        self.c.message_out(msg)
        if msg == '/quit\n':
            self.disconnect()
        self.input.delete('1.0', 'end')

    def disconnect(self):
        self.win.destroy()
        # self.c.disconnect()
        self.c.sock.close()
        exit(0)

    def resive(self):
        while True:
            try:
                msg = self.c.sock.recv(self.c.bufSize).decode('utf-8')
                # print(self.c.sock)
                # self.disconnect()
                if self.done:
                    if msg.split()[0] == "/Down":
                        filename = msg.split()[1]
                        port = int(msg.split()[2])
                        size = int(msg.split()[3])
                        self.c.files(filename, port, size)
                    print(f'user {self.name} received message: {msg}')
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', msg)
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except Exception as e:
                print(e)
                break


g = GUI()
