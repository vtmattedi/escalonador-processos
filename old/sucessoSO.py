import time
import os
import random
from abc import ABC, abstractmethod
from collections import deque
from tabulate import tabulate
import console

SOBRECARGA = 1
QUANTUM = 2
NOMES_PROCESSOS = ["Transmissao Dados", "Controle Freio", "Processamento Imagem", "Navegacao GPS"]

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

class Processo:
    def __init__(self, nome, chegada, duracao, prioridade=0, deadline=9999, custo=0):
        self.nome = nome
        self.chegada = chegada
        self.duracao = duracao
        self.restante = duracao
        self.inicio = -1
        self.fim = -1
        self.prioridade = prioridade
        self.deadline = deadline
        self.custo = custo
        self.timeline = []
        self.concluido = False
        self.sobrecarga = False

    def executar_um_minuto(self):
        if self.restante > 0:
            self.restante -= 1
            if self.restante == 0:
                self.concluido = True

class Escalonador(ABC):
    def __init__(self, tempo_real=False):
        self.processos = []
        self.concluidos = []
        self.tempo = 0
        self.tempo_real = tempo_real
        self.processos_chegados = set()
        self.processos_execucao = None
        self.nome_algoritmo = ""

    def adicionar(self, processo):
        self.processos.append(processo)

    def avancar_tempo(self, minutos=1):
        for _ in range(minutos):
            if self.tempo_real:
                time.sleep(0.6)
            self.tempo += 1
            self.checar_chegadas()

    def checar_chegadas(self):
        for p in self.processos:
            if p.chegada == self.tempo and p.nome not in self.processos_chegados:
                print(f"[{self.tempo} min] Processo {p.nome} chegou e está aguardando.")
                self.processos_chegados.add(p.nome)

    def mostrar_info_processos(self, colunas=None):
        if colunas is None:
            colunas = ["Processo", "Chegada", "Duração"]  # Colunas padrão mínimas
            
        dados = []
        for p in self.processos:
            linha = []
            for coluna in colunas:
                if coluna == "Processo":
                    linha.append(p.nome)
                elif coluna == "Chegada":
                    linha.append(p.chegada)
                elif coluna == "Duraçao":
                    linha.append(p.duracao)
                elif coluna == "Prioridade":
                    linha.append(p.prioridade)
                elif coluna == "Deadline":
                    linha.append(p.deadline)
                elif coluna == "Bilhetes":
                    linha.append(max(1, 10 - p.duracao))
                elif coluna == "Custo":
                    linha.append(p.custo)
            dados.append(linha)
        return tabulate(dados, headers=colunas, tablefmt="grid")

    def imprimir_tela_completa(self):
        limpar_tela()
        print(f"\nAlgoritmo: {self.nome_algoritmo} | Tempo: {self.tempo}\n")
        console.hprint(self.mostrar_info_processos())
        print("\nEstado da Execução:")
        self.imprimir_timeline(clear=False)

    def imprimir_timeline(self, clear=True):
        if clear:
            limpar_tela()
        print(f"Algoritmo: {self.nome_algoritmo}\n")
        print(f"Tempo: {self.tempo}\n")
        for p in self.processos:
            linha = " ".join(p.timeline)
            print(f"{p.nome:20}: {linha}")

    def metricas(self, algoritmo=None):
        print("\nResumo da execução:")
        tempos_resposta = []  
        tempos_espera = []
        tempos_sobrecarga = []
        
        for p in self.concluidos:
            sobrecarga = p.timeline.count('~')
            espera = p.timeline.count('░')  # Somente tempo na fila de prontos
            resposta = p.fim - p.chegada
            
            tempos_resposta.append(resposta)
            tempos_espera.append(espera)
            tempos_sobrecarga.append(sobrecarga)
            
            print(f"{p.nome}: Chegada={p.chegada}, Início={p.inicio}, Fim={p.fim}")
            print(f"  Tempo de Resposta (Turnaround): {resposta} min (chegada→fim)")
            print(f"  Tempo de Espera na Fila: {espera} min (símbolos ░)")
            print(f"  Tempo de Sobrecarga: {sobrecarga} min (símbolos ~)")
            print(f"  Tempo de Execução: {p.duracao} min")
            
            if algoritmo == "EDF":
                print(f"  Deadline: {p.deadline} min")
                if resposta <= p.deadline:
                    print("  ✅ Deadline CUMPRIDO (turnaround ≤ deadline)")
                else:
                    print(f"  ❌ Deadline NÃO CUMPRIDO (turnaround {resposta} > {p.deadline})")
            elif algoritmo == "Loteria":
                print(f"  Bilhetes: {max(1, 10 - p.duracao)}")
            elif algoritmo == "Prioridade":
                print(f"  Prioridade: {p.prioridade}")
            print("")
        
        if tempos_resposta:
            media_resposta = sum(tempos_resposta) / len(tempos_resposta)
            media_espera = sum(tempos_espera) / len(tempos_espera)
            media_sobrecarga = sum(tempos_sobrecarga) / len(tempos_sobrecarga)
            
            print(f"\nMétricas médias:")
            print(f"  Turnaround médio: {media_resposta:.2f} min")
            print(f"  Espera médio na fila: {media_espera:.2f} min")
            print(f"  Sobrecarga média: {media_sobrecarga:.2f} min")
            print(f"  Throughput: {len(self.concluidos)/self.tempo:.2f} processos/min")

class FIFO(Escalonador):
    def mostrar_info_processos(self):
        return super().mostrar_info_processos(["Processo", "Chegada", "Duraçao"])
    
    def escalonar(self):
        self.nome_algoritmo = "FIFO"
        print("\n" + "="*50)
        print("Iniciando FIFO")
        print("="*50)
        
        self.imprimir_tela_completa()
        input("\nPressione Enter para iniciar...")
        
        self.processos.sort(key=lambda p: p.chegada)
        
        while len(self.concluidos) < len(self.processos):
            processo_em_execucao = None

            for p in self.processos:
                if p.restante > 0 and p.chegada <= self.tempo:
                    processo_em_execucao = p
                    break

            if processo_em_execucao:
                p = processo_em_execucao
                if p.inicio == -1:
                    p.inicio = self.tempo
                    print(f"[{self.tempo} min] Iniciando {p.nome}")

                while p.restante > 0:
                    self.processos_execucao = p
                    
                    for proc in self.processos:
                        if proc == p:
                            proc.timeline.append("█")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")

                    self.imprimir_tela_completa()
                    print(f"\r[{self.tempo} min] Executando {p.nome}... restante: {p.restante} min", end="", flush=True)
                    
                    p.executar_um_minuto()
                    self.avancar_tempo()

                p.fim = self.tempo
                p.concluido = True
                self.concluidos.append(p)

            else:
                print(f"[{self.tempo} min] Ocioso")
                for proc in self.processos:
                    if proc.concluido:
                        proc.timeline.append("X")
                    elif proc.chegada <= self.tempo:
                        proc.timeline.append("░")
                    else:
                        proc.timeline.append(" ")
                self.imprimir_tela_completa()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_tela_completa()
        self.metricas()

class SJF(Escalonador):
    def mostrar_info_processos(self):
        return super().mostrar_info_processos(["Processo", "Chegada", "Duraçao"])
    
    def escalonar(self):
        self.nome_algoritmo = "SJF"
        print("\n" + "="*50)
        print("Iniciando SJF")
        print("="*50)
        
        self.imprimir_tela_completa()
        input("\nPressione Enter para iniciar...")
        
        fila = []
        processos_restantes = sorted(self.processos, key=lambda p: p.chegada)
        idx = 0

        while len(self.concluidos) < len(self.processos):
            while idx < len(processos_restantes) and processos_restantes[idx].chegada <= self.tempo:
                fila.append(processos_restantes[idx])
                idx += 1

            if fila:
                fila.sort(key=lambda p: p.duracao)
                p = fila.pop(0)

                if p.inicio == -1:
                    p.inicio = self.tempo
                    print(f"[{self.tempo} min] Iniciando {p.nome}")

                while p.restante > 0:
                    self.processos_execucao = p
                    
                    for proc in self.processos:
                        if proc == p:
                            proc.timeline.append("█")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")

                    self.imprimir_tela_completa()
                    print(f"\r[{self.tempo} min] Executando {p.nome}... restante: {p.restante} min", end="", flush=True)
                    
                    p.executar_um_minuto()
                    self.avancar_tempo()

                p.fim = self.tempo
                p.concluido = True
                self.concluidos.append(p)
            else:
                print(f"[{self.tempo} min] Ocioso")
                for proc in self.processos:
                    if proc.concluido:
                        proc.timeline.append("X")
                    elif proc.chegada <= self.tempo:
                        proc.timeline.append("░")
                    else:
                        proc.timeline.append(" ")
                self.imprimir_tela_completa()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_tela_completa()
        self.metricas()

class RoundRobin(Escalonador):
    def mostrar_info_processos(self):
        return super().mostrar_info_processos(["Processo", "Chegada", "Duraçao"])
    
    def escalonar(self):
        self.nome_algoritmo = "Round Robin"
        print("\n" + "="*50)
        print("Iniciando Round Robin")
        print("="*50)
        
        self.imprimir_tela_completa()
        input("\nPressione Enter para iniciar...")
        
        fila = deque()
        processos = sorted(self.processos, key=lambda p: p.chegada)
        idx = 0

        while len(self.concluidos) < len(self.processos):
            while idx < len(processos) and processos[idx].chegada <= self.tempo:
                fila.append(processos[idx])
                idx += 1

            if fila:
                p = fila.popleft()

                if p.inicio == -1:
                    p.inicio = self.tempo
                    print(f"[{self.tempo} min] Iniciando {p.nome}")

                quantum = 0
                while p.restante > 0 and quantum < QUANTUM:
                    self.processos_execucao = p
                    
                    for proc in self.processos:
                        if proc == p:
                            proc.timeline.append("█")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")

                    self.imprimir_tela_completa()
                    print(f"\r[{self.tempo} min] Executando {p.nome}... restante: {p.restante} min", end="", flush=True)
                    
                    p.executar_um_minuto()
                    self.avancar_tempo()
                    quantum += 1

                if p.restante > 0:
                    while idx < len(processos) and processos[idx].chegada <= self.tempo:
                        fila.append(processos[idx])
                        idx += 1
                    
                    print(f"\n[{self.tempo} min] Quantum expirado. Preemptando {p.nome}")
                    fila.append(p)
                    
                    for proc in self.processos:
                        if proc == p:
                            proc.timeline.append("~")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")
                    
                    self.imprimir_tela_completa()
                    self.avancar_tempo()
                else:
                    p.fim = self.tempo
                    p.concluido = True
                    self.concluidos.append(p)
            else:
                print(f"[{self.tempo} min] Ocioso")
                for proc in self.processos:
                    if proc.concluido:
                        proc.timeline.append("X")
                    elif proc.chegada <= self.tempo:
                        proc.timeline.append("░")
                    else:
                        proc.timeline.append(" ")
                self.imprimir_tela_completa()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_tela_completa()
        self.metricas()

class Prioridade(Escalonador):
    def mostrar_info_processos(self):
        return super().mostrar_info_processos(["Processo", "Chegada", "Duraçao", "Prioridade"])
    
    def escalonar(self):
        self.nome_algoritmo = "Prioridade (Não-Preemptivo)"
        print("\n" + "="*50)
        print("Iniciando Prioridade Não-Preemptivo")
        print("="*50)
        
        self.imprimir_tela_completa()
        input("\nPressione Enter para iniciar...")
        
        fila = []
        processos_restantes = sorted(self.processos, key=lambda p: p.chegada)
        idx = 0

        while len(self.concluidos) < len(self.processos):
            while idx < len(processos_restantes) and processos_restantes[idx].chegada <= self.tempo:
                fila.append(processos_restantes[idx])
                idx += 1

            if fila:
                fila.sort(key=lambda p: (p.prioridade, p.chegada))
                p = fila.pop(0)

                if p.inicio == -1:
                    p.inicio = self.tempo
                    print(f"[{self.tempo} min] Iniciando {p.nome} (prioridade: {p.prioridade})")

                while p.restante > 0:
                    self.processos_execucao = p
                    
                    for proc in self.processos:
                        if proc == p:
                            proc.timeline.append("█")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")

                    self.imprimir_tela_completa()
                    print(f"\r[{self.tempo} min] Executando {p.nome}... restante: {p.restante} min", end="", flush=True)
                    
                    p.executar_um_minuto()
                    self.avancar_tempo()

                p.fim = self.tempo
                p.concluido = True
                self.concluidos.append(p)
                
            else:
                print(f"[{self.tempo} min] Ocioso")
                for proc in self.processos:
                    if proc.concluido:
                        proc.timeline.append("X")
                    elif proc.chegada <= self.tempo:
                        proc.timeline.append("░")
                    else:
                        proc.timeline.append(" ")
                self.imprimir_tela_completa()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_tela_completa()
        self.metricas(algoritmo="Prioridade")

class EDF(Escalonador):
    def mostrar_info_processos(self):
        return super().mostrar_info_processos(["Processo", "Chegada", "Duraçao", "Deadline"])
    
    def escalonar(self):
        self.nome_algoritmo = "EDF (Preemptivo)"
        print("\n" + "="*50)
        print("Iniciando EDF Preemptivo")
        print("="*50)
        
        self.imprimir_tela_completa()
        input("\nPressione Enter para iniciar...")
        
        fila = []
        processos_restantes = sorted(self.processos, key=lambda p: p.chegada)
        idx = 0

        while len(self.concluidos) < len(self.processos):
            while idx < len(processos_restantes) and processos_restantes[idx].chegada <= self.tempo:
                fila.append(processos_restantes[idx])
                idx += 1

            if fila:
                fila.sort(key=lambda p: p.deadline)
                p = fila.pop(0)

                if p.inicio == -1:
                    p.inicio = self.tempo
                    print(f"[{self.tempo} min] Iniciando {p.nome} (deadline: {p.deadline})")

                quantum = 0
                while p.restante > 0 and quantum < QUANTUM:
                    self.processos_execucao = p
                    
                    for proc in self.processos:
                        if proc == p:
                            proc.timeline.append("█")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")

                    self.imprimir_tela_completa()
                    print(f"\r[{self.tempo} min] Executando {p.nome}... restante: {p.restante} min", end="", flush=True)
                    
                    p.executar_um_minuto()
                    self.avancar_tempo()
                    quantum += 1

                if p.restante > 0 and quantum == QUANTUM:
                    print(f"\n[{self.tempo} min] Quantum expirado. Preemptando {p.nome}")

                    for proc in self.processos:
                        if proc == p:
                            proc.timeline.append("~")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")

                    self.imprimir_tela_completa()
                    self.avancar_tempo()
                    fila.append(p)
                elif p.restante == 0:
                    p.fim = self.tempo
                    p.concluido = True
                    self.concluidos.append(p)
            else:
                print(f"[{self.tempo} min] Ocioso")
                for proc in self.processos:
                    if proc.concluido:
                        proc.timeline.append("X")
                    elif proc.chegada <= self.tempo:
                        proc.timeline.append("░")
                    else:
                        proc.timeline.append(" ")
                self.imprimir_tela_completa()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_tela_completa()
        self.metricas(algoritmo="EDF")

class EscalonadorLoteria(Escalonador):
    def mostrar_info_processos(self):
        return super().mostrar_info_processos(["Processo", "Chegada", "Duraçao", "Bilhetes"])
    
    def escalonar(self):
        self.nome_algoritmo = "Loteria Justa (Preemptivo)"
        print("\n" + "="*50)
        print("Iniciando Loteria Justa Preemptivo")
        print("="*50)
        
        self.imprimir_tela_completa()
        input("\nPressione Enter para iniciar...")
        
        processos_restantes = sorted(self.processos, key=lambda p: p.chegada)
        idx = 0
        bilhetes = {}
        processo_atual = None
        tempo_execucao = 0
        
        while len(self.concluidos) < len(self.processos):
            while idx < len(processos_restantes) and processos_restantes[idx].chegada <= self.tempo:
                novo_processo = processos_restantes[idx]
                bilhetes[novo_processo] = max(1, 10 - novo_processo.duracao)
                print(f"[{self.tempo} min] Processo {novo_processo.nome} chegou e recebeu {bilhetes[novo_processo]} bilhetes")
                idx += 1

            if processo_atual is None or tempo_execucao >= QUANTUM or processo_atual.concluido:
                if processo_atual and not processo_atual.concluido and tempo_execucao >= QUANTUM:
                    print(f"[{self.tempo} min] ⚡ Sobrecarga (~) - Quantum expirado para {processo_atual.nome}")
                    for proc in self.processos:
                        if proc == processo_atual:
                            proc.timeline.append("~")
                        elif proc.concluido:
                            proc.timeline.append("X")
                        elif proc.chegada <= self.tempo:
                            proc.timeline.append("░")
                        else:
                            proc.timeline.append(" ")
                    self.imprimir_tela_completa()
                    self.avancar_tempo()

                elegiveis = {p: t for p, t in bilhetes.items() if not p.concluido and p.chegada <= self.tempo}
                
                if elegiveis:
                    
                    total_bilhetes = sum(elegiveis.values())
                    sorteio = random.randint(1, total_bilhetes)
                    acumulado = 0
                    
                    for processo, num_bilhetes in elegiveis.items():
                        acumulado += num_bilhetes
                        if acumulado >= sorteio:
                            novo_vencedor = processo
                            break

                    if processo_atual != novo_vencedor and processo_atual is not None:
                        print(f"[{self.tempo} min] 🔄 Trocando de {processo_atual.nome} para {novo_vencedor.nome}")
                    
                    processo_atual = novo_vencedor
                    tempo_execucao = 0
                    
                    if processo_atual.inicio == -1:
                        processo_atual.inicio = self.tempo
                        print(f"[{self.tempo} min] 🎟️ Processo {processo_atual.nome} ganhou a loteria! (bilhetes: {bilhetes[processo_atual]})")
                else:
                    processo_atual = None

            if processo_atual:
                self.processos_execucao = processo_atual
                processo_atual.executar_um_minuto()
                tempo_execucao += 1
                
                for proc in self.processos:
                    if proc == processo_atual:
                        proc.timeline.append("█")
                    elif proc.concluido:
                        proc.timeline.append("X")
                    elif proc.chegada <= self.tempo:
                        proc.timeline.append("░")
                    else:
                        proc.timeline.append(" ")
                
                self.imprimir_tela_completa()
                print(f"[{self.tempo} min] Executando {processo_atual.nome}... restante: {processo_atual.restante} min")
                
                if processo_atual in bilhetes:
                    bilhetes[processo_atual] = max(1, bilhetes[processo_atual] - 1)
                    for p in elegiveis:
                        if p != processo_atual:
                            bilhetes[p] += 1
                
                if processo_atual.restante == 0:
                    processo_atual.fim = self.tempo
                    processo_atual.concluido = True
                    self.concluidos.append(processo_atual)
                    del bilhetes[processo_atual]
                    processo_atual = None
                    tempo_execucao = 0
                
                self.avancar_tempo()
            else:
                print(f"[{self.tempo} min] Ocioso (sem processos para loteria)")
                for proc in self.processos:
                    if proc.concluido:
                        proc.timeline.append("X")
                    else:
                        proc.timeline.append(" ")
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_tela_completa()
        self.metricas(algoritmo="Loteria Preemptivo")

class Simulador:
    @staticmethod
    def criar_processos_aleatorios():
        n_processos = random.randint(1, 4)
        nomes = random.sample(NOMES_PROCESSOS, n_processos)
        processos = []
        for nome in nomes:
            chegada = random.randint(0, 10)
            duracao = random.randint(1, 10)
            prioridade = random.randint(1, 10)
            deadline = chegada + random.randint(1, 20)
            custo = random.randint(1, 10)
            processos.append(Processo(nome, chegada, duracao, prioridade, deadline, custo))
        processos.sort(key=lambda p: p.chegada)
        print("\nProcessos gerados (aleatórios):")
        for p in processos:
            print(f"{p.nome}: chegada={p.chegada}, duração={p.duracao}, prioridade={p.prioridade}, deadline={p.deadline}, custo={p.custo}")
        print("")
        return processos

    @staticmethod
    def executar_todos():
        algoritmos = [EDF, FIFO, SJF, RoundRobin, Prioridade, EscalonadorLoteria]
        for algoritmo in algoritmos:
            processos = Simulador.criar_processos_aleatorios()
            escalonador = algoritmo(tempo_real=True)
            escalonador.nome_algoritmo = algoritmo.__name__
            for p in processos:
                escalonador.adicionar(p)
            escalonador.escalonar()
            print("\n" + "="*50)
            print(f"Fim da simulação com {algoritmo.__name__}")
            print("="*50 + "\n")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    Simulador.executar_todos()