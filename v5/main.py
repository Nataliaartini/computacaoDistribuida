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

class Pessoa:
    def __init__(self, rg, nome, hash_armazenado):
        self.hash_armazenado = hash_armazenado
        self.rg = rg
        self.nome = nome

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
        self.tabela_hash = {}
        self.total_tabela_hash = 0
        self.tabela_roteamento = tabela_roteamento

    def run(self):
        # cria o socket para comunicação usando SocketServer
        self.server = SocketServer(self.host, MessageHandler)
        self.server.process_message = self.processa_mensagem
        server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        server_thread.start()
        print(f"Processo PID: {self.pid} conectado...")

        if self.is_input:
            opcao = "-1"
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
                    self.envia_mensagem(Mensagem(self.pid, "PRI", -1, None, None), nodo_vizinho)

                elif opcao == "3":
                    rg = input("Digite o RG de quem deseja buscar: ")
                    hash = self.calcular_hash(rg)
                    nodo = self.buscar_nodo_por_hash(hash)
                    if nodo.pid == self.pid:
                        usuario = self.retornar_usuario(hash)
                        print("RG: " + usuario.rg, " NOME: " + usuario.nome)
                    else:
                        self.envia_mensagem(Mensagem(self.pid, "PRI", hash, None, None), nodo_vizinho)




        # ao encerrar o processo libera os recursos
        #self.server.shutdown()
        #server_thread.join()

    def printar_usuarios(self):
        for i in range(21):
            if self.tabela_hash.get(i) is not None:
                print("IN. " + "[" + str(i) + "] RG: " + self.tabela_hash[i].rg, " NOME: " + self.tabela_hash[i].nome)

    def retornar_usuario(self, hash):
        return self.tabela_hash[hash]
    
    def buscar_nodo_por_id(self, pid):
        for item in self.tabela_roteamento:
            if item.no.pid == pid:
                return item.no

    def buscar_intervalos_por_nodo_id(self, pid):
        for item in self.tabela_roteamento:
            if item.no.pid == pid:
                return item

    def buscar_nodo_por_hash(self, hash):
        for item in self.tabela_roteamento:
            if item.inicial <= hash and item.final >= hash:
                return item.no
    
    def inserir_pessoa(self, rg, nome):
        hash = self.calcular_hash(rg)
        self.inserir_pessoa_by_hash(rg, nome, hash)

    def inserir_pessoa_by_hash(self, rg, nome, hash):
        if self.total_tabela_hash >= 10:
            print("PROCESSO " + str(self.pid) + " - ESTA CHEIO")

        nodo = self.buscar_nodo_por_hash(hash)
        if nodo.pid == self.pid:
            if self.total_tabela_hash < 10:
                if self.tabela_hash.get(hash) is None:
                    self.tabela_hash[hash] = Pessoa(rg, nome, hash)
                    self.total_tabela_hash += 1
                else:
                    novo_hash = ((hash+1) % 21)
                    if novo_hash == 0:
                        novo_hash = 1
                    self.inserir_pessoa_by_hash(rg, nome, novo_hash)
            else:
                novo_hash = hash
                intervalo = self.buscar_intervalos_por_nodo_id(self.pid)
                if(intervalo.inicial == 1):
                    novo_hash = 11
                else:
                    novo_hash = 1

                self.envia_mensagem(Mensagem(self.pid, "INS", novo_hash, Pessoa(rg, nome, novo_hash), None), nodo)
        else:
            self.envia_mensagem(Mensagem(self.pid, "INS", hash, Pessoa(rg, nome, hash), None), nodo)


    def calcular_hash(self, rg):
        return int(rg) % 20 + 1

    def processa_mensagem(self, mensagem):
        mensagem = pickle.loads(mensagem)  # recebe a mensagem
        if mensagem.tipo == "INS":
            self.inserir_pessoa_by_hash(mensagem.usuario.rg, mensagem.usuario.nome, mensagem.hash)
        elif mensagem.tipo == "PRI" and mensagem.hash > 0:
            usuarios = []
            usuarios.append(self.retornar_usuario(mensagem.hash))
            for item in self.tabela_roteamento:
                if item.no.pid != self.pid:
                    self.envia_mensagem(Mensagem(self.pid, "RET", mensagem.hash, None, usuarios), item.no)
                    return
            
        elif mensagem.tipo == "PRI":
            usuarios = []
            for i in range(21):
                if self.tabela_hash.get(i) is not None:
                    usuarios.append(self.tabela_hash[i])

            for item in self.tabela_roteamento:
                if item.no.pid != self.pid:
                    self.envia_mensagem(Mensagem(self.pid, "RET", mensagem.hash, None, usuarios), item.no)
                    return

        elif mensagem.tipo == "RET" and mensagem.hash > 0:
            for item in mensagem.usuarios:
                print("RG: " + item.rg, " NOME: " + item.nome)
        elif mensagem.tipo == "RET":
            nodo = self.buscar_nodo_por_id(self.pid)
            if nodo.pid == 1:
                self.printar_usuarios()

            for item in mensagem.usuarios:
                print("EX. " + "[" + str(item.hash_armazenado) + "] RG: " + item.rg, " NOME: " + item.nome)

            if nodo.pid != 1:
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
n1 = Nodo(1, ("localhost", 12347), tabela_roteamento, True)
n2 = Nodo(2, ("localhost", 12348), tabela_roteamento, False)
tabela_roteamento += [TabelaRoteamento(n1, 1, 10), TabelaRoteamento(n2, 11, 20)]
n1.start()
n2.start()
#time.sleep(random.randint(4, 7))

#threading.Timer(60, lambda: [no.stop() for no in [n1, n2]]).start()