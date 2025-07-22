
from abc import ABC, abstractmethod
from collections import OrderedDict

def logToFile(text):
    with open("escalonador.log", "a") as f:
        f.write(text + "\n")



class algoritimo_base(ABC):
    def __init__(self):
        self.name_algoritmo = self.__class__.__name__

    @abstractmethod
    def escalonar(self, processos):
        """
        Método responsável por escalonar os processos.
        """
        raise NotImplementedError("Este método deve ser implementado por subclasses.")
    

class escalonador_fcfs(algoritimo_base):
    def __init__(self):
        super().__init__()
        self.name = "FCFS"

    def escalonar(self, processos, tempo_atual):
        # Ordena os processos por tempo de chegada
        if not processos:
            return None
        return sorted(processos, key=lambda p: p.chegada)[0]

class escalonador_sjf(algoritimo_base):
    def __init__(self):
        super().__init__()
        self.name = "SJF"

    def escalonar(self, processos, tempo_atual):
        # Ordena os processos por tempo restante
        # Caso não seja preemptivo, tempo restante = burst time
        if not processos:
            return None
        return sorted(processos, key=lambda p: (p.restante, p.prioridade))[0]

class escalonador_rr(algoritimo_base):
    #escalonador Round Robin

    def __init__(self):
        super().__init__()
        # Quantum é o time slice do escalonador
        self.name = "RR"
        self.fila = OrderedDict() # Fila de processos RR
    def escalonar(self, processos, tempo_atual):
        # Adiciona novos processos ao final da fila
        # Se o processo já estiver na fila, não o adiciona novamente
        for processo in processos:
            if processo.nome not in self.fila:
                self.fila[processo.nome] = processo

        # Remove processos que não estão mais na lista de processos
        self.fila = {k: v for k, v in self.fila.items() if v in processos}
        # retorna o primeiro processo da fila
        res = next(iter(self.fila.values())) if self.fila else None
        if res is not None:
            del self.fila[res.nome]  # dequeue
            self.fila[res.nome] = res  # Rotaciona o primeiro processo para o final

        return res

    
class escalonador_priority(algoritimo_base):
    def __init__(self):
        super().__init__()
        self.name = "Priority"

    def escalonar(self, processos, tempo_atual):
        # Ordena os processos por prioridade e tempo de chegada
        if not processos:
            return None
        return sorted(processos, key=lambda p: (p.prioridade, p.chegada))[0]

class escalonador_edf(algoritimo_base):
    def __init__(self):
        super().__init__()
        self.name = "EDF"

    def escalonar(self, processos, tempo_atual):
        # Ordena os processos por deadline e prioridade
        if not processos:
            return None
        return sorted(processos, key=lambda p: (p.deadline, p.prioridade))[0]

class escalonador_lottery(algoritimo_base):
    def __init__(self):
        super().__init__()
        self.name = "Lottery"
        self.tickets = {}
        self.last_process = set()
    # Reorna um processo aleatório da lista de processos
    # Cada processo tem um número de tickets, que é decrementado a cada vez que o processo é selecionado
    # O numero incial de tickets é 10 - burst time do processo
    # O processo selecionado perde 1 ticket e os outros ganham 1 ticket.
    # Atualmente só funciona com sistema single core.
    def escalonar(self, processos, tempo_atual):
        # adiciona novos processos à lista de tickets
        for p in processos:
            if p not in self.tickets:
                n_tickets = max(1, 10 - p.duracao)
                self.tickets[p] = n_tickets
                  
        # Remove processos que não estão mais na lista de processos
        self.tickets = {p: t for p, t in self.tickets.items() if p in processos}
        
        if not processos:
            return None 
        
        res = [item for item, weight in self.tickets.items() for _ in range(weight)][0]

        # Decrementa o ticket do processo selecionado e incrementa os outros
        for p in self.tickets:
            if p == res:
                self.tickets[p] = max(1, self.tickets[p] - 1)
            else:
                self.tickets[p] += 1

        return res

class escalonador_hrrn(algoritimo_base):
    def __init__(self):
        super().__init__()
        self.name = "HRRN"

    def escalonar(self, processos, tempo_atual):
        if not processos:
            return None
        def hrrn_score(p, tempo_atual):
            """Calcula o score HRRN para um processo"""
            espera = tempo_atual - p.chegada
            return (espera + p.restante) / p.restante if p.restante > 0 else float('inf')
        return sorted(processos, key=lambda p: (-hrrn_score(p, tempo_atual)))[0]
