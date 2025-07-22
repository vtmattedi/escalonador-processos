import time
import os
import random
from abc import ABC, abstractmethod
from collections import deque
import console
SOBRECARGA = 1
QUANTUM = 2
NOMES_PROCESSOS = ["Transmissao Dados", "Controle Freio", "Processamento Imagem", "Navegacao GPS"]

def limpar_tela():
    console.clear_screen()
    
def print_frame(frame):
    console.home()
    _frames = frame.split('\n')
    i = 0
    for a_frame in _frames:
        i += 1
        console.fprint(a_frame)
    for _ in range(i, os.get_terminal_size().lines - 1):
        console.fprint("")

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
                # print(f"[{self.tempo} min] Processo {p.nome} chegou e está aguardando.")
                self.processos_chegados.add(p.nome)

    def imprimir_timeline(self, text = ""):
        # if clear:
        #     limpar_tela()
        frame = f"Algoritmo: {self.nome_algoritmo}\n"
        frame += f"Tempo: {self.tempo}\n"
        for p in self.processos:
            linha = " ".join(p.timeline)
            frame += f"{p.nome:20}: {linha}\n"
        frame += "\n"
        frame += text
        print_frame(frame)

    def metricas(self, algoritmo=None):
        print("\nResumo da execução:")
        for p in self.concluidos:
            turnaround = p.fim - p.chegada
            resposta = p.inicio - p.chegada
            espera = turnaround - p.duracao
            print(f"{p.nome}: Chegada={p.chegada}, Início={p.inicio}, Fim={p.fim}")
            print(f"  Turnaround: {turnaround} min, Resposta: {resposta} min, Espera: {espera} min")
            if algoritmo == "EDF":
                print(f"  Execução: {p.duracao} min, Deadline: {p.deadline}\n")
            elif algoritmo == "Leilao":
                print(f"  Execução: {p.duracao} min, Custo: {p.custo}\n")
            elif algoritmo == "Prioridade":
                print(f"  Execução: {p.duracao} min, Prioridade: {p.prioridade}\n")
            else:
                print(f"  Execução: {p.duracao} min\n")

class FIFO(Escalonador):
    def escalonar(self):
        print("\nFIFO em tempo real\n")
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

                    frame = f"[{self.tempo} min] Executando {p.nome}... restante: {p.restante} min"
                    self.imprimir_timeline(frame)

                    
                    p.executar_um_minuto()
                    self.avancar_tempo()

                p.fim = self.tempo
                p.concluido = True
                self.concluidos.append(p)

            else:
                for proc in self.processos:
                    if proc.concluido:
                        proc.timeline.append("X")
                    elif proc.chegada <= self.tempo:
                        proc.timeline.append("░")
                    else:
                        proc.timeline.append(" ")
                self.imprimir_timeline(f"[{self.tempo} min] Ocioso")
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_timeline()
        self.metricas()

class SJF(Escalonador):
    def escalonar(self):
        print("\nSJF em tempo real\n")
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

                    self.imprimir_timeline()
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
                self.imprimir_timeline()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_timeline()
        self.metricas()

class RoundRobin(Escalonador):
    def escalonar(self):
        print("\nRound Robin em tempo real\n")
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

                    self.imprimir_timeline()
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

                    self.imprimir_timeline()
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
                self.imprimir_timeline()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_timeline()
        self.metricas()

class Prioridade(Escalonador):
    def escalonar(self):
        print("\nPrioridade em tempo real\n")
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

                    self.imprimir_timeline()
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

                    self.imprimir_timeline()
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
                self.imprimir_timeline()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_timeline()
        self.metricas(algoritmo="Prioridade")

class EscalonadorPorLeilao(Escalonador):
    def escalonar(self):
        print("\nLeilão em tempo real\n")
        processos_nao_concluidos = sorted(self.processos, key=lambda p: p.chegada)
        idx = 0

        while len(self.concluidos) < len(self.processos):
            while idx < len(processos_nao_concluidos) and processos_nao_concluidos[idx].chegada <= self.tempo:
                idx += 1

            elegiveis = [p for p in self.processos if p.chegada <= self.tempo and not p.concluido]

            if elegiveis:
                p = max(elegiveis, key=lambda x: (x.custo, -x.chegada))

                if p.inicio == -1:
                    p.inicio = self.tempo
                    print(f"[{self.tempo} min] Vencedor do leilão: {p.nome} (custo: {p.custo})")

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

                    self.imprimir_timeline()
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
                self.imprimir_timeline()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_timeline()
        self.metricas(algoritmo="Leilao")

class EDF(Escalonador):
    def escalonar(self):
        print("\nEDF em tempo real\n")
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

                    self.imprimir_timeline()
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

                    self.imprimir_timeline()
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
                self.imprimir_timeline()
                self.avancar_tempo()

        self.processos_execucao = None
        self.imprimir_timeline()
        self.metricas(algoritmo="EDF")


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
            deadline = chegada + random.randint(1, 10)
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
        algoritmos = [FIFO, SJF, RoundRobin, Prioridade, EscalonadorPorLeilao, EDF]
        for algoritmo in algoritmos:
            processos = Simulador.criar_processos_aleatorios()
            escalonador = algoritmo(tempo_real=True)
            escalonador.nome_algoritmo = algoritmo.__name__
            for p in processos:
                escalonador.adicionar(p)
            escalonador.escalonar()
            print("=" * 50 + "\n")
            time.sleep(3)

if __name__ == "__main__":
    console.show_cursor(False)
    try:
        Simulador.executar_todos()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        console.show_cursor(True)