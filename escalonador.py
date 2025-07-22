import os
import time

from math import floor
from algoritimos import algoritimo_base, logToFile
from snapshot import snapshot as Snapshot
from task import TaskState, TarefaCAV
import console
from enum import Enum

class instantType(Enum):
    OVERLOAD = 0
    WAITING = 1
    HALF_WAITING = 2
    EXECUTING = 3
    FINALIZED = 4
    NOT_ON_LIST = 5

def instantTypeToColor(type):
    return {
        instantType.OVERLOAD: "41",  # Red background
        instantType.WAITING: "43",   # Yellow background
        instantType.HALF_WAITING: "43",  # Yellow background
        instantType.EXECUTING: "42", # Green background
        instantType.FINALIZED: "44", # Blue background
        instantType.NOT_ON_LIST: "0" 
    }.get(type, "0")


class escalonador:
    def __init__(self, algoritmo, preemptivo, time_slice=1, sobrecarga=0.6):
        if not isinstance(algoritmo, algoritimo_base):
            raise TypeError("Algoritmo deve ser uma instância de algoritimo_base")
        self.preemptivo = preemptivo
        self.tarefas = []
        self.algoritmo = algoritmo
        self.tempo = 0
        self.current_task = None
        self.time_slice = time_slice  # Tempo de slice para escalonamento
        self.overload_cost = sobrecarga # Custo de sobrecarga
        self.at_overload = False  # Callback para sobrecarga
        self.n_overload = 0  # Contador de sobrecargas
        self.snapshots = []  # Lista de snapshots para armazenar o estado do escalonador
    
    def adicionar_tarefa(self, tarefa):
        self.tarefas.append(tarefa)

    def tick(self):
        """Executa o algoritmo de escalonamento e retorna a próxima tarefa a ser executada."""
        if not self.tarefas:
            return 
        
        if self.current_task is not None and self.current_task.restante <= 0:
            self.current_task.estado = TaskState.FINALIZADO

        # Filtra as tarefas prontas e que já chegaram
        valid_tasks = [t for t in self.tarefas if t.chegada <= self.tempo]
        # Filtra as tarefas que não estão finalizadas
        valid_tasks = [t for t in valid_tasks if t.estado != TaskState.FINALIZADO]
        # Algoritimo não preemptivo:
        if not self.preemptivo:
            #Se estiver executando uma tarefa, não escalona outra
            if self.current_task is not None and self.current_task.estado == TaskState.EXECUTANDO:
                pass
            else:
                self.current_task = self.algoritmo.escalonar(valid_tasks, self.tempo)
        # Algoritimo preemptivo:
        else:
            # Se estamos em sobrecarga, não escalona outra tarefa
            if self.at_overload:
                self.at_overload = False  # Reseta o estado de sobrecarga
                pass
            # Se há tarefas válidas, escalona uma nova tarefa
            else:
            # Se não há tarefa atual ou a tarefa atual está finalizada, escalona uma nova
                if self.current_task is not None and self.current_task.estado == TaskState.EXECUTANDO:
                    self.current_task.estado = TaskState.PRONTO  # Marca a tarefa atual como pronta
                    valid_tasks.append(self.current_task)  # Re-adiciona a tarefa atual se ela não estiver finalizada
                    self.at_overload = True  # Marca que estamos em sobrecarga
                # Se não há tarefa atual ou a tarefa atual está finalizada, escalona uma nova
                self.current_task = self.algoritmo.escalonar(valid_tasks, self.tempo)
        # Se temos sobrecarga, adiciona o custo de sobrecarga ao tempo
        if self.at_overload:
            self.n_overload += 1
            self.tempo += self.overload_cost
            return
        # Executa a tarefa atual se houver
        if self.current_task:
            self.current_task.estado = TaskState.EXECUTANDO
            self.tempo += self.current_task.executar(self.tempo, self.time_slice)
        else:
            #senão houver tarefa atual, apenas avança o tempo
            # para o proximo tick inteiro
            self.tempo = floor(self.tempo + self.time_slice)  # Avança o tempo se não houver tarefa atual
        return
    def print_history(self):
        """Imprime o histórico de snapshots do escalonador."""
        preemptable =  "Preemptável" if self.preemptivo else "Não Preemptável"
        preemptable = console.italic(preemptable)
        CYAN = "36"  # Cyan color for preemptable status
        MAGENTA = "35"  # Magenta color for non-preemptable status
        preemptable = console.insert_color(preemptable, CYAN if self.preemptivo else MAGENTA)
        
        line = f"Simulando {self.algoritmo.name} ({preemptable}): "
        line += console.bold(f"T: {self.tempo:2.1f} ")
        line += f"{console.italic('t.u.')}"
        frame = console.hcenter(line)
        names = [t.nome for t in self.snapshots[0].processos]
        max_len = max(len(name) for name in names)
        max_len = max(max_len, 10)  # Ensure minimum length for task names
        task_header = console.hcenter("Tarefas", max_len + 2 + 2)

        # task_frame += "\n" + "-"* (max_len + 2)
        max_ticks = (os.get_terminal_size().columns - len(task_header)) // 6
        task_frame = ""
        for name in names:
            task_frame += f"\n\033[1;37m{name.rjust(max_len)}\033[0m "
            task_frame += "\n" + "-"* (max_len + 2) 
        task_frame= task_frame[1:]
        task_h = []
        v_div = console.uline("|") + "\n|"* ((len(names) - 1)* 2 ) + "\n-"
       
        last_exec = None
        for i, s in enumerate(self.snapshots):
            # imprime apenas os últimos max_ticks snapshots
            if len(self.snapshots) - i > max_ticks:
                continue
            this_time = []
            for t in s.processos:
                logToFile(f"Processo: {t.nome}, last_exec: {last_exec}")
                if s.at_overload and t.nome == last_exec:
                    this_time.append(instantType.OVERLOAD)
                elif t.estado == TaskState.EXECUTANDO:
                    last_exec = t.nome
                    logToFile(f"Tarefa {last_exec} está executando no tempo {s.tempo}")
                    this_time.append(instantType.EXECUTING)
                elif t.estado == TaskState.PRONTO and s.tempo > t.chegada:
                    last_t = self.snapshots[i - 1].tempo if i > 0 else 0
                    if last_t < t.chegada:
                        this_time.append(instantType.HALF_WAITING)
                    else:
                        this_time.append(instantType.WAITING)
                elif t.estado == TaskState.FINALIZADO:
                    this_time.append(instantType.FINALIZED)
                else:
                    this_time.append(instantType.NOT_ON_LIST)
            SLOT_LEN = 5 
            if s.at_overload:
                    SLOT_LEN = floor( self.overload_cost /self.time_slice * SLOT_LEN)
                    SLOT_LEN = max(SLOT_LEN, 3)
            diff = SLOT_LEN + 1
            
            time_str =  f'{s.tempo:1.1f}'.rjust(diff)
            
            task_header += time_str
            slice = ""
            for t in this_time:
                task_color = instantTypeToColor(t)
                if t == instantType.HALF_WAITING:
                    half = floor(SLOT_LEN / 2)
                    slice += f"\n\033[{0}m{' ' * half}\033[0m"  + f"\033[{task_color}m{' ' * (SLOT_LEN - half)}\033[0m"
                else:
                    slice += f"\n\033[{task_color}m{' ' * SLOT_LEN}\033[0m"
                slice += "\n" + "-" * SLOT_LEN
            
            task_h.append(slice[1:])
        task_frame = console.mergeLines(task_frame, v_div, 0)
        for spr in task_h:
            task_frame = console.mergeLines(task_frame, spr, 0)
            task_frame = console.mergeLines(task_frame, v_div, 0)
       
        frame +=  "\n\n" + console.insert_color(task_header, "1;4")
        frame += "\n" + task_frame
        # table = console.table(headers=TarefaCAV.__dict__.keys(), rows=[t.__dict__.values() for t in self.tarefas])
        # frame += "\n\n" + console.hcenter(table)
        lcount = os.get_terminal_size().lines - 1
        console.home()
        for line in frame.split("\n"):
            lcount -= 1
            console.fprint(line)
        for i in range(lcount):
            console.fprint("")

    def take_snapshot(self):
        """Tira um instantâneo do estado atual do escalonador."""
        self.snapshots.append(Snapshot(self.tarefas, self.tempo, self.algoritmo, self.preemptivo, self.at_overload))
        self.print_history()
    def simular_sync(self, delay=0.5):
        """Executa o escalonador até todas as tarefas serem finalizadas."""
        
        while not all(t.estado == TaskState.FINALIZADO for t in self.tarefas):
            self.tick()
            self.take_snapshot()
            time.sleep(delay)
        
    
    def resultado(self):
        results = {}
        # tira um time slice pois tem mais um ts para mostrar todos finalizados
        results["tempo_total"] = self.tempo - self.time_slice
        results["n_overload"] = self.n_overload
        results["total_overload_time"] = self.overload_cost * self.n_overload
        results["n_processos"] = len(self.tarefas)

        results["avg_turnaround_time"] = sum(t.turn_around_time for t in self.tarefas if t.turn_around_time is not None) / len(self.tarefas)
        results["avg_turnaround_time"] = f"{results['avg_turnaround_time']:.2f}"
        results["avg_wait_time"] = sum(t.wait_time for t in self.tarefas if t.wait_time is not None) / len(self.tarefas)
        results["avg_wait_time"] = f"{results['avg_wait_time']:.2f}"
        results["avg_response_time"] = sum(t.response_time for t in self.tarefas if t.response_time is not None) / len(self.tarefas)
        results["avg_response_time"] = f"{results['avg_response_time']:.2f}"
        return results
