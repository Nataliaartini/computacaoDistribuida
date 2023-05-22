import socket
import socketserver
import threading
import random
import pickle
from enum import Enum
import time

# tempo em segundos para aguardar a simulação de falha
LEADER_CRASH_DELAY = 6

class Mensagens(Enum):
    ELECTION = "ELECTION"
    LEADER = "LEADER"
    VICTORY = "VICTORY"
    OK = "OK"

class SocketServer(socketserver.ThreadingTCPServer):
    pass

class MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        message = self.request.recv(1024).decode()
        self.server.process_message(message)

class Process(threading.Thread):
    def __init__(self, pid, host, procs):
        super().__init__()
        self.pid = pid
        self.host = host
        self.ativo = True
        self.eh_coordenador = False
        self.processo_coordenador = None
        self.procs_conectados = procs
        self.eleicao_iniciada = False

    def run(self):
        # cria o socket para comunicação usando SocketServer
        self.server = SocketServer(self.host, MessageHandler)
        self.server.process_message = self.processa_mensagem
        server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        server_thread.start()

        # mantém o processo ativo
        while self.ativo:
            pass

        # ao encerrar o processo libera os recursos
        self.server.shutdown()
        server_thread.join()


    def processa_mensagem(self, full_message):
        sender, message = full_message.split("-")
        sender = int(sender)

        time.sleep(random.randint(1, 5))

        # quando recebe mensagem de ELEICAO responde com OK se estiver ativo
        # pois sabe que veio de um PID menor
        if message == Mensagens.ELECTION.value:
            if self.ativo:
                procs = [p for p in self.procs_conectados if p.pid == sender]
                self.envia_mensagem(Mensagens.OK, procs)

        # quando recebe OK é porque outro processo está requisitando a liderança
        # desiste da eleicao
        elif message == Mensagens.OK.value:
            print(f"Proc. {self.pid} recebeu OK (PID: {sender}).")
            self.eh_coordenador = False
            proc = [p for p in self.procs_conectados if p.pid == sender][0]

            # processo que enviou OK deveria iniciar nova eleicao ?
            if not self.eh_coordenador and self.processo_coordenador is None:
                proc.inicia_eleicao()

        # quando recebe uma mensagem de LEADER há um novo coordenador
        elif message == Mensagens.LEADER.value:
            print(f"Proc. {self.pid} recebeu uma mensagem do novo COORDENADOR (PID: {sender}).")
            self.eh_coordenador = False
            self.processo_coordenador = [p for p in self.procs_conectados if p.pid == sender][0]

    def inicia_eleicao(self):
        print(f"Proc. {self.pid} iniciou uma ELEIÇÃO.")
        self.eleicao_iniciada = True
        # se o processo atual está rodando
        if self.ativo:
            highest_id_process = max([p.pid for p in self.procs_conectados])

            # verifica se o processo atual possui o maior ID
            if self.pid == highest_id_process:
                self.declara_vitoria()
            else:
                self.envia_mensagem(Mensagens.ELECTION, [p for p in self.procs_conectados if p.pid > self.pid])

    def declara_vitoria(self):
        print(f"Processo {self.pid} se declara como COORDENADOR.")
        self.eh_coordenador = True
        self.processo_coordenador = [p for p in self.procs_conectados if p.pid == self.pid][0]
        self.envia_mensagem(Mensagens.LEADER)

    def envia_mensagem(self, message, procs=None):
        # possibilita enviar mensagem para um ou vários dependendo do parametro
        if procs is None:
            procs = self.procs_conectados
        for proc in procs:
            if proc.host != self.host and proc.ativo:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect(proc.host)
                        sock.sendall(f"{self.pid}-{message.value}".encode())
                except socket.error as e:
                    print(f"Impossivel enviar mensagem PID: {proc.pid}-{proc.host}")
                    print(e)
                    continue

    def wait(self):
        print(f"Processo {self.pid} aguardando...")

    def simula_parada(self):
        if self.eh_coordenador:
            # Randomize the crash delay within a certain range
            crash_delay = random.randint(LEADER_CRASH_DELAY - 5, LEADER_CRASH_DELAY + 5)
            print(f"Process {self.pid} will simulate leader crash in {crash_delay} seconds...")
            self.stop()

    def stop(self):
        self.ativo = False
        print(f"Processo {self.pid} se despede.")


SOCKET_ADDRESS = 12345
SOCKET_HOST = 'localhost'
NUM_PROCS = 5

# cria a lista de processos para demonstração
processes = []
for i in range(NUM_PROCS):
    address = (SOCKET_HOST, SOCKET_ADDRESS + i)
    proc = Process(i + 1, address, processes)
    processes.append(proc)
    proc.start()


# escolhe um processo aleatório para iniciar a eleição
proc = processes[random.randint(0, NUM_PROCS-1)]
proc.inicia_eleicao()


# para os processos depois de um tempo para não consumir recursos
threading.Timer(20, lambda: [proc.stop() for proc in processes if proc.ativo]).start()
