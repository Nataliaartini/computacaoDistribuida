import socket
import threading
import sys

HOST = "127.0.0.1"
PORT1 = int(sys.argv[1])
PORT2 = int(sys.argv[2])

stream_lock = threading.Lock()

def cliente():
    stream_lock.acquire()
    usuario = input("Digite seu nome: ")
    stream_lock.release()
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((HOST, PORT2))

    c.sendall(str.encode(usuario, "utf8"))
    while True:
        texto = input()
        textoBytes = str.encode(texto, "utf8")
        if not texto:
            break
        c.sendall(textoBytes)
    c.close()

def servidor():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind((HOST,PORT1))
        s.listen()
        stream_lock.acquire()
        print(f'Server rodando em {HOST}:{PORT1}')
        stream_lock.release()

        clientExternoNome = ''
        client, address = s.accept()
        while True:
            receiveMessageFromClient = client.recv(1024).decode('utf8')
            if clientExternoNome != '':
                stream_lock.acquire()
                print(f'{clientExternoNome}-> {receiveMessageFromClient}')
                stream_lock.release()
                if not receiveMessageFromClient:
                    break
            else:
                clientExternoNome = receiveMessageFromClient
        s.close()
    except:
        pass

thread1 = threading.Thread(target=servidor,args=()) 
thread2 = threading.Thread(target=cliente,args=())
thread1.start()
thread2.start()