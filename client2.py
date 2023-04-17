# echo-client.py

import socket
import threading

HOST = "127.0.0.1"
PORT = 1313

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

usuario = input("Digite seu nome: ")
s.connect((HOST, PORT))

def enviar():
    while True:
        texto = input()
        textoBytes = str.encode(texto, "utf8")
        s.sendall(textoBytes)

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