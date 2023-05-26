import socket
import threading
from cryptography.fernet import Fernet
import time


HOST = '127.0.0.1'
PORT = 55552
ADDRESS = r"C:\Users\afekv\PycharmProjects\chat\database.txt"
USERS = {}
KEY = Fernet.generate_key()
FERNET = Fernet(KEY)
DATA = []


def add_info_to_database(data):
    DATA.append(data)
    msg_data = ''.join([str(item) for item in DATA])
    enc_message = FERNET.encrypt(msg_data.encode())

    file = open(ADDRESS, "wb")
    file.write(enc_message)
    file.close()


def send_database(client_socket):
    file = open(ADDRESS, "rb")
    data = file.read()
    file.close()

    dec_message = FERNET.decrypt(data).decode()
    client_socket.send(dec_message.encode())


def broadcast(message, client_name):
    for client in USERS:
        if client != client_name:
            USERS[client].send(f"{client_name}: {message}".encode())
        else:
            USERS[client_name].send(f"You: {message}".encode())


def client_connection():
    while True:
        client_socket, address = server.accept()

        client_socket.send("username".encode())
        username = client_socket.recv(1024).decode()
        print(f"\n{username} joined the chat")

        USERS[username] = client_socket
        for client_sock in USERS.values():
            if client_socket != client_sock:
                client_sock.send(f"{username} joined the chat\n".encode())
            else:
                client_socket.send("You joined the chat\n".encode())

        add_info_to_database(f"{username} joined the chat\n")

        thread = threading.Thread(target=message_receiver, args=(client_socket,))
        thread.start()


def message_receiver(client_socket):
    time.sleep(0.1)
    send_database(client_socket)
    while True:
        try:
            message = client_socket.recv(1024).decode()
            username = list(USERS.keys())[list(USERS.values()).index(client_socket)]

            add_info_to_database(f"{username}: {message}")
            broadcast(message, username)
        except:
            username = list(USERS.keys())[list(USERS.values()).index(client_socket)]
            USERS.pop(username)
            client_socket.close()
            add_info_to_database(f'{username} left the chat\n')
            broadcast(f'{username} left the chat\n', client_socket)
            break


if __name__ == '__main__':
    file = open(ADDRESS, 'w')
    file.close()                # cleans database

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server running...")
    client_connection()
