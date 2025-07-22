import random
import time
from collections import deque
from abc import ABC, abstractmethod
from old.Tarefas import TarefaCAV
import CAV
from esclonadores import EscalonadorFIFO, EscalonadorRoundRobin, EscalonadorPrioridade
# Função para criar algumas tarefas fictícias
def criar_tarefas():
    tarefas = [
        TarefaCAV("Detecção de Obstáculo", random.randint(5, 10), prioridade=1),
        TarefaCAV("Planejamento de Rota", random.randint(3, 6), prioridade=2),
        TarefaCAV("Manutenção de Velocidade", random.randint(2, 5), prioridade=3),
        TarefaCAV("Comunicando com Infraestrutura", random.randint(4, 7), prioridade=1)
    ]
    return tarefas



# Exemplo de uso
if __name__ == "__main__":
    # Criar algumas tarefas fictícias
    tarefas = criar_tarefas()

    # Criar um CAV.CAV
    cav = CAV.CAV(id=1)
    for t in tarefas:
        cav.adicionar_tarefa(t)

    # Criar um escalonador FIFO
    print("Simulando CAV.CAV com FIFO:\n")
    escalonador_fifo = EscalonadorFIFO()
    for t in tarefas:
        escalonador_fifo.adicionar_tarefa(t)

    simulador_fifo = CAV.CAV(id=1)
    simulador_fifo.executar_tarefas(escalonador_fifo)

    # Criar um escalonador Round Robin com quantum de 3 segundos
    print("\nSimulando CAV.CAV com Round Robin:\n")
    escalonador_rr = EscalonadorRoundRobin(quantum=3)
    for t in tarefas:
        escalonador_rr.adicionar_tarefa(t)

    simulador_rr = CAV.CAV(id=1)
    simulador_rr.executar_tarefas(escalonador_rr)

    # Criar um escalonador por Prioridade
    print("\nSimulando CAV.CAV com Escalonamento por Prioridade:\n")
    escalonador_prio = EscalonadorPrioridade()
    for t in tarefas:
        escalonador_prio.adicionar_tarefa(t)

    simulador_prio = CAV.CAV(id=1)
    simulador_prio.executar_tarefas(escalonador_prio)
