import random
from enum import Enum

class TaskState(Enum):
    PRONTO = "pronto"
    EXECUTANDO = "executando"
    FINALIZADO = "finalizado"

class TarefaCAV:
    def __init__(self, nome, chegada, duracao, deadline = None, prioridade=0):
        self.color = random.randint(0, 255)  # Random color for terminal output
        self.nome = nome # Nome da tarefa 
        self.prioridade = prioridade # Prioridade da tarefa (quanto menor o número, maior a prioridade)
        self.chegada = chegada # Tempo de chegada
        self.duracao = duracao # Burst time
        self.deadline = chegada + (deadline if deadline is not None else float('inf')) # Deadline is optional, defaults to infinity
        self.restante = duracao # Tempo restante para completar a tarefa
        self.estado = TaskState.PRONTO  # Estado inicial do processo
        self.response_time = None # Tempo de resposta 1ra execução
        self.turn_around_time = None # Tempo de retorno
        self.wait_time = None # Tempo de espera
        self.taskFailed = False # Indica se a tarefa falhou (estourou deadline)
        # self.coreAfinity = None  # pinneToCore
        # self.softCoreAfinity = None  # set and managed by the SO to avoid task migration 

    def executar(self, tempo_atual, time_slice=1, continue_after_deadline=True):
        tempo_execucao = min(self.restante, time_slice)

        # Set the response time on the first execution
        if self.duracao == self.restante:
            self.response_time = tempo_atual - self.chegada
        # Executa a tarefa por um tempo de 'time_slice' ou até terminar
        if self.restante > 0:
            self.restante -= time_slice
        tempo = tempo_atual + tempo_execucao
        if tempo > self.deadline and self.restante > 0:
            self.taskFailed = True # indica que a tarefa estorou deadline
            if not continue_after_deadline:
                self.finished(tempo)
   
            # self.estado = TaskState.FINALIZADO
            # self.turn_around_time = tempo - self.chegada
            # self.wait_time = self.turn_around_time - self.duracao + self.restante
        if self.restante == 0:
            self.finished(tempo)

        return tempo_execucao

    def finished(self, end_time):
        self.turn_around_time = end_time - self.chegada
        self.wait_time = self.turn_around_time - self.duracao
    def __str__(self):
        return f"{self.nome} (Prioridade: {self.prioridade}, Chegada: {self.chegada}, Duração: {self.duracao}, Deadline: {self.deadline}, Estado: {self.estado})"