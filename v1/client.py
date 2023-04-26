# echo-client.py

import socket
import threading

HOST = "127.0.0.1"
PORT = 1313

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

usuario = input("Digite seu nome: ")
#fazer uma função pra definir o ID do usuário
s.connect((HOST, PORT))

def regiaoCritica():
    isRegiaoCritica = 0
    #implementar a função de eleição que decide qual processo(ID) vai rodar

def enviar():
    while True:
        texto = input()
        textoBytes = str.encode(texto, "utf8")
        s.sendall(textoBytes)

        #chamar a função de cima pra ver se pode acessar o server

def receber():
    while True:
        mensagem = s.recv(1024).decode("utf8")
        if mensagem =='getUser':
            textoBytes = str.encode(usuario, "utf8")
            s.send(textoBytes)
        else:
            print(mensagem)

thread1 = threading.Thread(target=receber,args=()) 
thread2 = threading.Thread(target=enviar,args=())
thread1.start()
thread2.start()