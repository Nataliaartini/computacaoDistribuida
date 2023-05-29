import socket
import socketserver
import threading
import random
import pickle
from enum import Enum
import time


class Mensagens(Enum):
    DEP = "dep100"
    JUR = "jur1%"
    ACK = "ack"


class SocketServer(socketserver.ThreadingTCPServer):
    pass


class MessageHandler(socketserver.BaseRequestHandler):
    #  função para manipular a mensagem trocada no servidor de socket
    def handle(self):
        message = self.request.recv(1024).decode("ISO-8859-1")
        self.server.process_message(bytes(message, "ISO-8859-1"))


class Mensagem(object):
    # mensagem trocada pelos processos
    def __init__(self, pid, op, tr):
        self.pid = pid  # processo que originou a mensagem
        self.sender = pid  # processo que esta enviando essa mensagem atualmente
        self.op = op  # operação solicitada
        self.tr = tr  # tempo relativo do processo que realizou a solicitação
        self.ack = False  # mensagem é do tipo ACK
        self.procs_reconhecidos = []  # processos que já reconheceram a mensagem


class Processo(threading.Thread):
    def __init__(self, pid, host, procs):
        super().__init__()
        self.pid = pid
        self.host = host
        self.server = None
        self.procs_conectados = procs
        self.fila_local = []
        self.saldo = 1000
        self.clock = 1
        self.ativo = True

    def run(self):
        # cria o socket para comunicação usando SocketServer
        self.server = SocketServer(self.host, MessageHandler)
        self.server.process_message = self.processa_mensagem
        server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        server_thread.start()

        time.sleep(random.randint(1, 3))
        print(f"Processo PID: {self.pid} conectado...")

        # mantém o processo ativo
        while self.ativo:
            # verifica se há processos na fila local
            if len(self.fila_local) > 0:
                time.sleep(3)
                self.executa_atualizacao()  # executa atualização de há processos na fila

        # ao encerrar o processo libera os recursos
        self.server.shutdown()
        server_thread.join()

    def processa_mensagem(self, mensagem):
        mensagem = pickle.loads(mensagem)  # recebe a mensagem

        if mensagem.ack == True:  # se for mensagem de ACK de mensagem anterior
            print(
                f"(PID: {self.pid}): Mensagem ACK recebida: Sender: (PID: {mensagem.sender}) - {mensagem.op.value}"
            )
            # verifica condição da fila local
            for proc in self.fila_local:
                if (
                    proc.pid == mensagem.pid
                    and proc.op == mensagem.op
                    and proc.tr == mensagem.tr
                ):
                    # se a mensagem estiver na fila local dos processos, inclui
                    # o processo que disparou o ACK na lista de processos que
                    # reconheceram a mensagem
                    proc.procs_reconhecidos.append(mensagem.sender)

        elif mensagem.op == Mensagens.DEP or mensagem.op == Mensagens.JUR:  # se for mensagem de atualização
            print(
                f"(PID: {self.pid}): Mensagem recebida: Sender: (PID: {mensagem.pid}) - {mensagem.op.value}"
            )
            # adiciona na fila local
            self.fila_local.append(mensagem)

    def solicita_atualizacao(self, operacao):
        # solicita atualizacao DEP ou JUR aos processos conectados
        for proc in self.procs_conectados:
            msg = Mensagem(self.pid, operacao, self.clock)
            if proc.ativo:  # envia somente se o processo esta ativo
                self.envia_mensagem(msg, proc)
        self.tick()

    def reconhece_atualizacao(self):
        # verifica na fila local as mensagens disponíveis
        for i, msg in enumerate(self.fila_local):
            # se o PID for menor ou igual ao PID do processo corrente
            # ou
            # a primeira mensagem (i = 0) e não tiver originado no próprio processo
            # verifica se ack não foi enviado
            if ((msg.pid <= self.pid) or (i == 0 and msg.pid != self.pid)) and msg.ack is False:
                msg.ack = True  # altera para envio de ack
                msg.sender = self.pid  # coloca o próprio processo como sender
                for proc in self.procs_conectados:
                    # envia para os processo conectados que estejam ativos
                    if proc.ativo:
                        self.envia_mensagem(msg, proc)

    def executa_atualizacao(self):
        procs_conectados = [p.pid for p in self.procs_conectados]
        # verifica se os processos conectados são os mesmos que já reconheceram a mensagem
        if sorted(self.fila_local[0].procs_reconhecidos) == sorted(procs_conectados):
            # remove atualização da fila
            message = self.fila_local.pop(0)
            print(
                f"(PID: {self.pid}) Executando atualização:  Sender: (PID: {message.pid}) - {message.op.value} "
            )
            # executa as mensagens
            if message.op == Mensagens.DEP:
                self.saldo += 100
            elif message.op == Mensagens.JUR:
                self.saldo += self.saldo * 0.01
            # emite um sinal de reconhecimento de atualizações caso haja alguma
            # na fila ainda sem reconhecer
            time.sleep(1)
            self.reconhece_atualizacao()

    def envia_mensagem(self, message, proc):
        # envia a mensagem
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(proc.host)
                sock.sendall(pickle.dumps(message))
        except socket.error as e:
            print(f"Impossivel enviar mensagem ao PID: {proc.pid}-{proc.host}")
            print(e)

    def imprime_fila_local(self):
        # imprime a fila local de cada processo para acompanhamento
        print(f"\n(PID: {self.pid}) - Fila Local (Clock: {self.clock})")
        for i, msg in enumerate(self.fila_local):
            print(
                f"Tempo: {i+1} - OP: {msg.op} - Sender: {msg.pid} - Reconhecidos: {msg.procs_reconhecidos}"
            )

    def imprime_saldo(self):
        # imprime o saldo da conta
        print(f"(PID: {self.pid}) - Saldo Local: R$ {self.saldo}")

    def tick(self):
        # faz o relógio do processo andar 1 posição lógica
        self.clock += 1

    def stop(self):
        # seta ativo para False para encerrar a thread e liberar recursos
        self.ativo = False
        print(f"(PID:{self.pid}): Processo se despede.")


SOCKET_PORT = 12345
SOCKET_HOST = "localhost"

processos = []
p1 = Processo(1, ("localhost", 12345), processos)
p2 = Processo(2, ("localhost", 12346), processos)
processos += [p1, p2]
p1.start()
p2.start()
time.sleep(random.randint(4, 7))

p1.solicita_atualizacao(Mensagens.DEP)
p2.solicita_atualizacao(Mensagens.JUR)
time.sleep(5)

p1.imprime_fila_local()
p2.imprime_fila_local()
time.sleep(3)

p1.reconhece_atualizacao()
p2.reconhece_atualizacao()
time.sleep(3)

p1.imprime_fila_local()
p2.imprime_fila_local()
time.sleep(15)

p1.imprime_saldo()
p2.imprime_saldo()

threading.Timer(60, lambda: [proc.stop() for proc in processos if proc.ativo]).start()
