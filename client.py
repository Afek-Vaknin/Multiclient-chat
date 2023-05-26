import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT = 55552


class Client:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("NICKNAME", "Please choose a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_threat = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_threat.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightblue")
        self.win.geometry("400x600")

        self.chat_label = tkinter.Label(self.win, text=f"{self.nickname}'s Chat", bg="lightpink")
        self.chat_label.config(font=("Ariel Black", 14))
        self.chat_label.pack(padx=1e0, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=10, pady=5)
        self.text_area.config(state='disabled')

        self.msg_chat = tkinter.Label(self.win, text="↓TYPE HERE↓", bg="lightyellow")
        self.msg_chat.config(font=("Times New Roman", 12))
        self.msg_chat.pack(padx=10, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=10, pady=5)

        self.send_button = tkinter.Button(self.win, text='SEND', command=self.write)
        self.send_button.config(font=('Ariel', 12))
        self.send_button.pack(padx=1, pady=1)

        self.gui_done = True

        self.win.mainloop()

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

    def write(self):
        message = f"{self.input_area.get('1.0', 'end')}"
        self.socket.send(message.encode())
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.socket.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.socket.recv(1024).decode()
                if message == 'username':
                    self.socket.send(self.nickname.encode('utf-8'))
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
                self.socket.close()
                break


if __name__ == "__main__":
    Client(HOST, PORT)
