# echo-server.py

import socket
import threading

HOST = "127.0.0.1"
PORT = 1313

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen()
print(f'Server rodando em {HOST}:{PORT}')

clients = []
usernames = []
IDusers = []

def globalMessage(message):
    for client in clients:
        client.send(message)

def handleMessages(client):
    while True:
        try:
            receiveMessageFromClient = client.recv(1024).decode('utf8')
            globalMessage(f'{usernames[clients.index(client)]}-> {receiveMessageFromClient}'.encode('utf8'))
        except:
            clientLeaved = clients.index(client)
            client.close()
            clients.remove(clients[clientLeaved])
            clientLeavedUsername = usernames[clientLeaved]
            print(f'{clientLeavedUsername} has left the chat...')
            globalMessage(f'{clientLeavedUsername} has left us...'.encode('utf8'))
            usernames.remove(clientLeavedUsername)

while True:
    try:
        client, address, IDuser = s.accept()
        print(f"New Connetion: {str(address)}")
        clients.append(client)
        client.send('getUser'.encode('utf8'))
        username = client.recv(1024).decode('utf8')
        usernames.append(username)

        IDusers.append(IDuser)
        IDuser = client.recv(1024)

        globalMessage(f'{username} just joined the chat!'.encode('utf8'))
        user_thread = threading.Thread(target=handleMessages,args=(client,))
        user_thread.start()
    except:
        pass