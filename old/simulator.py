
from snapshot import snapshot
from task import TarefaCAV
import console
import os
import time

# Data structure to hold statistics
# Python needs better json support
# Either be C++ or be JS, it is the worst of both worlds

class DataStruct:
    def __init__(self):
        self.algoritmo = None
        self.preemptable = None
        self.context_switches = None
        self.total_time = None
        self.num_processes = None
        self.avg_waiting_time = None
        self.avg_turnaround_time = None
        self.avg_response_time = None
        self.failed_processes = None
        
    def safe_str(self):
        string = f"{self.algoritmo} ({'Preemptable' if self.preemptable else 'Non-Preemptable'})\n"
        for key, value in self.__dict__.items():
            if key == "algoritmo" or key == "preemptable":
                continue  # Skip the 'algoritmo' key and 'preemptable' key
            if value is not None:
                string += f"\t {key}: {value} \n"
        return string[:-1]  # Remove last newline character

class Simulator():
    def __init__(self, escalonador, preemptable, time_slice=1):
        super().__init__()
        self.time_slice = time_slice
        self.processos_disponiveis = set()
        self.processos = set()
        self.tempo = 0
        self.escalonador = escalonador
        self.current_task = None
        self.preemptable = preemptable
        self.context_switches = 0
        self.snapshots = [] # List to hold snapshots of the simulation state useful if I one day implement a timeline
        self.last_snapshot = None
        self.take_snapshot()  # Take an initial snapshot
    
    def take_snapshot(self):
        s = snapshot(self.processos, self.tempo, self.escalonador, self.preemptable, self.context_switches, self.processos_disponiveis)
        self.snapshots.append(s)
        self.last_snapshot = s

    def adicionar_processo(self, processo):
        self.processos.add(processo)

    def tick(self):
        # Atualiza o estado dos processos disponíveis
        for job in self.processos:
            if self.tempo >= job.chegada and job not in self.processos_disponiveis and job.estado == TaskState.FUTURO:
                job.estado = TaskState.PRONTO
                self.processos_disponiveis.add(job)
        # Se o escalonador não for preemptável, não faz nada até a tarefa atual terminar
        if self.current_task is not None and not self.preemptable:
            pass
        else:
            # pede para o escalonador ordenar os processos disponíveis
            if self.current_task is not None:
                self.current_task.estado = TaskState.PRONTO
            p = self.escalonador.escalonar(self.processos_disponiveis)
            if p:
                # Isso faz com que escalar a mesma logica para mais processadores seja facil.
                # self.current_task seria uma lista de processos e 
                # pegaria N_CORES processos do escalonador
                if self.current_task != p[0]:
                    self.context_switches += 1
                self.current_task = p[0]
                self.current_task.estado = TaskState.EXECUTANDO
        if (self.context_switches > 0 and self.preemptable) or (self.current_task is not None and self.current_task.estado == TaskState.EXECUTANDO):
            self.tempo += 1
            self.troca_contexto = True
        # Precisa ser aqui pois depois desse ponto, o tempo avança
        self.take_snapshot()  # Take a snapshot after each tick
        
        self.tempo += self.time_slice
        if self.current_task is not None:
            self.current_task.executar(self.tempo, self.time_slice)
            if self.current_task.estado == TaskState.FINALIZADO:
                self.processos_disponiveis.remove(self.current_task)
                self.current_task = None
   
       

    def print_frame(self, frame):
        console.home()
        lcount = 1
        for line in frame.splitlines():
            console.fprint(line)
            lcount += 1
        for _ in range(os.get_terminal_size().lines - lcount):
            console.fprint("")
    def print_snapshot(self, snapshot=None):
        console.home()
        frame = f"Algoritmo: {snapshot.escalonador} Preemptivel: {snapshot.preemptable}\n"
        frame += f"Tempo: {snapshot.tempo}\n"
        frame += f"Trocas de Contexto: {snapshot.context_switches}\n"
        frame += f"Processos Disponíveis: {len(snapshot.processos_disponiveis)}\n"
        for processo in snapshot.processos_disponiveis:
            frame += f" - {processo.nome} (Estado: {processo.estado})\n"
        frame += "Todos Processos:\n"
        for p in snapshot.processos:
            frame += f" - {p.nome}: {p.estado}\n"
        lcount = 1
        for line in frame.split("\n")[:-1]:
            lcount += 1
            console.fprint(line)
        for _ in range(os.get_terminal_size().lines - lcount):
            console.fprint("")
            
    def start_sync(self, sleep_time=0.5):
        def all_processes_finished():
                return all(p.estado == TaskState.FINALIZADO for p in self.processos)
        while not all_processes_finished():
            self.tick()
            self.print_snapshot(self.last_snapshot)
            time.sleep(sleep_time)
        self.take_snapshot()  # Take a final snapshot after the simulation ends
        self.print_snapshot(self.last_snapshot)
        time.sleep(sleep_time)


    def calc_stat(self, context_cost=0):
        data = DataStruct()
        data.algoritmo = self.escalonador.name
        data.preemptable = self.preemptable
        data.total_time = self.tempo + context_cost * self.context_switches
        data.context_switches = self.context_switches
        data.num_processes = len(self.processos)
        data.avg_waiting_time = 0
        data.avg_turnaround_time = 0
        data.avg_response_time = 0
        data.failed_processes = len([p for p in self.processos if p.taskFailed])
        total_waiting_time = 0
        total_turnaround_time = 0
        total_response_time = 0
        for p in self.processos:
            turnaround_time = p.turn_around_time if p.turn_around_time is not None else 0
            waiting_time = p.wait_time if p.wait_time is not None else 0
            total_waiting_time += waiting_time 
            total_turnaround_time += turnaround_time
            total_response_time += p.response_time if p.response_time is not None else 0
        data.avg_waiting_time = total_waiting_time / len(self.processos) if self.processos else 0
        data.avg_turnaround_time = total_turnaround_time / len(self.processos) if self.processos else 0
        data.avg_response_time = total_response_time / len(self.processos) if self.processos else 0
        return data
