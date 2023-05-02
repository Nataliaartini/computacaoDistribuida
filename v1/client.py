import socket
import threading

HOST = "127.0.0.1"
PORT = 1313

SPATH = 'tmp'#em principio lugar para guardar os processos??

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

usuario = input("Digite seu nome: ")
#fazer uma função pra definir o ID do usuário
s.connect((HOST, PORT))

def enviar():
    try:
        texto = input()
        textoBytes = str.encode(texto, "utf8")
        s.sendall(textoBytes + ';' + HOST) #??
        return 1
    except:
        return 0

def regiaoCritica(coordenador):
    while True:
        ## Verifica se o coordenador esta ativo
        status = enviar(coordenador,'1')
        if status == 0:
            print 'Coodenador parado '+str(coordenador)+'. Iniciando Eleicao'
            list = os.listdir(SPATH)
            for processo in list:
                if int(processo) > int(HOST):
                    status = enviar(processo,'E')
                    if status == 0:
                        print 'Erro enviando E ao processo ' + processo
            break
        else:
            print 'Conectou no coordenador ' + coordenador
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