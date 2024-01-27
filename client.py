import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import rsa

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

class Client:

    def __init__ (self, host, port, public_partner):
        
        # each client has a socket and it connects to host and port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # recieving public key from server
        self.public_partner = rsa.PublicKey.load_pkcs1(self.sock.recv(1024))

        # ask client for their name
        msg = tkinter.Tk()
        msg.withdraw()

        self.name = simpledialog.askstring("please choose a name", msg)

        # flag for gui being built
        self.gui_done = False

        # flag for running connection
        self.running = True

        # thread for building a gui for client and maintainings
        gui_thread = threading.Thread(target=self.gui_loop)

        # thread for dealing with the server connection
        recieve_thread = threading.Thread(target=self.recieve)

        gui_thread.start()
        recieve_thread.start()

    def gui_loop(self):

        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = f"{self.name}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(rsa.encrypt(message.encode(), self.public_partner))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def recieve(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode()
                if message == 'NAME':
                    self.sock.send(self.name.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                self.running = False
                break

client = Client(HOST, PORT, public_partner=None)