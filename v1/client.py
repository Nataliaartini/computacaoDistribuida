import socket
import threading
import os
import sys
import random

HOST = "127.0.0.1"
PORT = 1313

SPATH = 'tmp'#em principio lugar para guardar os processos?? acho que nao vai precisar??

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IDuser = random.randint(1,99)
usuario = input("Digite seu nome: ")

s.connect((HOST, PORT))

def enviar():
    # try:
    while True:
        texto = input('digite aqui: ')
        textoBytes = str.encode(texto, "utf8")
        s.sendall(textoBytes)# + ';' + HOST) #??
        # return 1
    # except:
    #     return 0

def regiaoCritica(coordenador):
    while True:
        ## Verifica se o coordenador esta ativo
        status = enviar(coordenador,'1')
        if status == 0:
            print('Coodenador parado '+str(coordenador)+'. Iniciando Eleicao')
            list = os.listdir(SPATH)
            for processo in list:
                if int(processo) > int(HOST):
                    status = enviar(processo,'E')
                    if status == 0:
                        print('Erro enviando E ao processo ' + processo)
            break
        else:
            print('Conectou no coordenador ' + coordenador)
    return 0

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