import random
import time
from collections import deque

# Para implementar um novo método de escalonamento, vocês devem criar uma nova classe que herda de Escalonador e implementar o método escalonar de acordo com sua estratégia.
# Este código fornece a base para que vocês experimentem e implementem suas próprias ideias de escalonamento, mantendo a estrutura flexível e fácil de estender.


class Processo:
    def __init__(self, nome, tempo_execucao):
        self.nome = nome
        self.tempo_execucao = tempo_execucao  # tempo total necessário para execução
        self.tempo_restante = tempo_execucao  # tempo restante para execução

    def __str__(self):
        return f"Processo {self.nome}: {self.tempo_execucao} unidades de tempo"

    def executar(self, quantum):
        """Executa o processo por um tempo de 'quantum' ou até terminar"""
        tempo_exec = min(self.tempo_restante, quantum)
        self.tempo_restante -= tempo_exec
        return tempo_exec

# Cada processo tem um nome, um tempo total de execução (tempo_execucao),
# e um tempo restante (tempo_restante), que é decrementado conforme o processo vai sendo executado.
# O método executar(quantum) executa o processo por uma quantidade limitada de tempo (quantum) ou até ele terminar.


class Escalonador:
    def __init__(self):
        self.processos = []
        self.sobrecarga = 0  # Inicializa a sobrecarga

    def adicionar_processo(self, processo):
        self.processos.append(processo)

    def escalonar(self):
        """Método de escalonamento a ser implementado pelos alunos"""
        raise NotImplementedError

    def registrar_sobrecarga(self, tempo):
        """Simula o acréscimo de tempo de sobrecarga"""
        self.sobrecarga += tempo

# A classe base Escalonador define a estrutura para os escalonadores, incluindo um método escalonar
# que vocês deverão implementar em suas versões específicas de escalonamento (como FIFO e Round Robin).


class FIFO(Escalonador):
    def __init__(self):
        super().__init__()

    def escalonar(self):
        """FIFO - First In First Out"""
        print("Iniciando escalonamento FIFO...\n")
        tempo_inicial = 0
        for processo in self.processos:
            processo.tempo_inicial = tempo_inicial
            tempo_inicial += processo.tempo_execucao
            processo.tempo_final = tempo_inicial
            print(f"Executando {processo.nome} de {processo.tempo_execucao} unidades.")
            time.sleep(processo.tempo_execucao)  # Simulando o tempo de execução
            print(f"{processo.nome} finalizado.\n")

        # No FIFO não há troca de contexto, logo a sobrecarga é zero
        print(f"Sobrecarga total no FIFO: {self.sobrecarga} unidades de tempo.")

# O escalonador FIFO executa os processos na ordem em que foram adicionados, sem interrupção, até que todos os processos terminem.


class RoundRobin(Escalonador):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        """Round Robin"""
        print("Iniciando escalonamento Round Robin...\n")
        fila = deque(self.processos)
        tempo_inicial = 0
        while fila:
            processo = fila.popleft()
            processo.tempo_inicial = tempo_inicial
            tempo_exec = processo.executar(self.quantum)
            tempo_inicial += tempo_exec
            if processo.tempo_restante > 0:
                fila.append(processo)  # Coloca o processo de volta na fila se não terminou
            processo.tempo_final = tempo_inicial
            print(f"Executando {processo.nome} por {tempo_exec} unidades.")
            time.sleep(tempo_exec)  # Simulando o tempo de execução

            # A cada troca de contexto, registramos a sobrecarga
            self.registrar_sobrecarga(1)  # Considerando 1 unidade de tempo para cada troca de contexto

            if processo.tempo_restante == 0:
                print(f"{processo.nome} finalizado.\n")
            else:
                print(f"{processo.nome} ainda precisa de {processo.tempo_restante} unidades.\n")

        print(f"Sobrecarga total no Round Robin: {self.sobrecarga} unidades de tempo.")

# O escalonador Round Robin permite que cada processo seja executado por um tempo limitado (quantum).
# Quando o processo termina ou o quantum é atingido, o próximo processo da fila é executado.
# Se o processo não terminar no quantum, ele é colocado de volta na fila.


class SimuladorEscalonamento:
    def __init__(self, escalonador: Escalonador):
        self.escalonador = escalonador

    def rodar_simulacao(self):
        self.escalonador.escalonar()

# A classe SimuladorEscalonamento é usada para rodar a simulação, passando o escalonador escolhido para o método rodar_simulacao().


# Função para criar alguns processos fictícios
def criar_processos():
    nomes = ["P1", "P2", "P3", "P4"]
    tempos = [random.randint(5, 10) for _ in nomes]  # Tempo de execução aleatório entre 5 e 10
    return [Processo(nomes[i], tempos[i]) for i in range(len(nomes))]

# Esta função cria uma lista de processos fictícios com nomes e tempos de execução aleatórios, usada para testar os escalonadores.


# Exemplo de uso:
if __name__ == "__main__":
    # Criar alguns processos
    processos = criar_processos()

    # Criar um escalonador FIFO
    print("Simulando FIFO:\n")
    fifo = FIFO()
    for p in processos:
        fifo.adicionar_processo(p)

    simulador_fifo = SimuladorEscalonamento(fifo)
    simulador_fifo.rodar_simulacao()

    # Criar um escalonador Round Robin com quantum de 3 unidades
    print("\nSimulando Round Robin:\n")
    rr = RoundRobin(quantum=3)
    for p in processos:
        rr.adicionar_processo(p)

    simulador_rr = SimuladorEscalonamento(rr)
    simulador_rr.rodar_simulacao()
