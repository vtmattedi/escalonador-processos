
class CAV:
    def __init__(self, id, escalonador=None):
        self.id = id  # Identificador único para cada CAV
        self.tarefas = []  # Lista de tarefas atribuídas a esse CAV
        self.escalonador = escalonador

    def adicionar_tarefa(self, tarefa):
        self.tarefas.append(tarefa)


    def simular(self, delay=0.5):
        if self.escalonador:
            for tarefa in self.tarefas:
                self.escalonador.adicionar_tarefa(tarefa)
            self.escalonador.simular_sync(delay)

