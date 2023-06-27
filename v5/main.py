import socket
import socketserver
import threading
import pickle
class SocketServer(socketserver.ThreadingTCPServer):
    pass


class MessageHandler(socketserver.BaseRequestHandler):
    #  função para manipular a mensagem trocada no servidor de socket
    def handle(self):
        message = self.request.recv(1024).decode("ISO-8859-1")
        self.server.process_message(bytes(message, "ISO-8859-1"))


class TabelaRoteamento:
    def __init__(self, no, inicial, final):
        self.no = no
        self.inicial = inicial
        self.final = final

class Mensagem(object):
    # mensagem trocada pelos processos
    def __init__(self, pid, tipo, hash, usuario, usuarios):
        self.pid = pid  # processo que originou a mensagem
        self.tipo = tipo #PRI OU INS
        self.hash = hash
        self.usuario = usuario
        self.usuarios = usuarios


class Nodo(threading.Thread):
    def __init__(self, pid, host, tabela_roteamento, is_input):
        super().__init__()
        self.pid = pid
        self.host = host
        self.server = None
        self.is_input = is_input
        self.tabela_hash = []
        self.tabela_roteamento = tabela_roteamento

    def run(self):
        # cria o socket para comunicação usando SocketServer
        self.server = SocketServer(self.host, MessageHandler)
        self.server.process_message = self.processa_mensagem
        server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        server_thread.start()
        print(f"Processo PID: {self.pid} conectado...")

        if self.is_input:
            while opcao != "0":
                print("""--------------------------
                Menu:
                1 - Cadastrar
                2 - Listar todos
                3 - Listar especifico
                0 - Sair
                --------------------------""")
                opcao = input()

                if opcao == "1":
                    rg = input("Digite o RG: ")
                    nome = input("Digite o nome: ")
                    self.inserir_pessoa(rg, nome)

                elif opcao == "2":
                    #nodo = self.buscar_nodo_por_id(self.pid)
                    #if nodo.inicial == 1:
                    #    self.printar_usuarios()
                    #else:
                    nodo_vizinho = self.buscar_nodo_por_hash(1)
                    self.envia_mensagem(Mensagem(self.pid, "PRI", -1, None), nodo_vizinho)

                elif opcao == "3":
                    rg = input("Digite o RG de quem deseja buscar: ")
                    hash = self.calcular_hash(rg)
                    nodo = self.buscar_nodo_por_hash(hash)
                    if nodo.pid == self.pid:
                        usuario = self.retornar_usuario(hash)
                        print("RG: " + usuario.rg, " NOME: " + usuario.nome)
                    else:
                        self.envia_mensagem(Mensagem(self.pid, "PRI", hash, None), nodo_vizinho)




        # ao encerrar o processo libera os recursos
        #self.server.shutdown()
        #server_thread.join()

    def printar_usuarios(self):
        for item in self.tabela_hash:
            print("RG: " + item.rg, " NOME: " + item.nome)

    def retornar_usuario(self, hash):
        return self.tabela_hash[hash]
    
    def buscar_nodo_por_id(self, pid):
        for item in self.tabela_roteamento:
            if item.pid == pid:
                return item.no


    def buscar_nodo_por_hash(self, hash):
        for item in self.tabela_roteamento:
            if item.inicial <= hash and item.final >= hash:
                return item.no
    
    def inserir_pessoa(self, rg, nome):
        hash = self.calcular_hash(rg)
        nodo = self.buscar_nodo_por_hash(hash)
        if nodo.pid == self.pid:
            self.tabela_hash[hash] = (rg, nome)
        else:
            self.envia_mensagem(Mensagem(self.pid, "INS", hash, (rg, nome)), nodo)

    def calcular_hash(self, rg):
        return int(rg) %  20 + 1

    def processa_mensagem(self, mensagem):
        mensagem = pickle.loads(mensagem)  # recebe a mensagem
        if mensagem.tipo == "ÏNS":
            self.tabela_hash[mensagem.hash] = mensagem.usuario
        elif mensagem.tipo == "PRI" and mensagem.hash > 0:
            usuarios = []
            usuarios.append(self.retornar_usuario(mensagem.hash))
            self.envia_mensagem(Mensagem(self.pid, "RET", mensagem.hash, None, usuarios))
        elif mensagem.tipo == "PRI":
            usuarios = self.tabela_hash
            self.envia_mensagem(Mensagem(self.pid, "RET", mensagem.hash, None, usuarios))
        elif mensagem.tipo == "RET" and mensagem.hash > 0:
            for item in mensagem.usuarios:
                print("RG: " + item.rg, " NOME: " + item.nome)
        elif mensagem.tipo == "RET":
            nodo = self.buscar_nodo_por_id(self.pid)
            if nodo.incial == 1:
                self.printar_usuarios()

            for item in mensagem.usuarios:
                print("RG: " + item.rg, " NOME: " + item.nome)

            if nodo.incial != 1:
                self.printar_usuarios()


    def envia_mensagem(self, message, proc):
        # envia a mensagem
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(proc.host)
                sock.sendall(pickle.dumps(message))
        except socket.error as e:
            print(f"Impossivel enviar mensagem ao PID: {proc.pid}-{proc.host}")
            print(e)

tabela_roteamento = []
n1 = Nodo(1, ("localhost", 12345), tabela_roteamento, True)
n2 = Nodo(2, ("localhost", 12346), tabela_roteamento, False)
tabela_roteamento += [TabelaRoteamento(n1, 1, 10), TabelaRoteamento(n2, 11, 20)]
n1.start()
n2.start()
#time.sleep(random.randint(4, 7))

threading.Timer(60, lambda: [no.stop() for no in [n1, n2]]).start()
#carla linda te amon 
