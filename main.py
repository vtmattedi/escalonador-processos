import copy
import algoritimos
from cav import CAV
from task import TarefaCAV
import argparse
import os
import json
import console
from escalonador import escalonador as Escalonador

# Caso o arquivo de entrada não seja especificado, utiliza os valores padrão:

# Algoritmos, Preemptabilidade
# Cada tupla contém o algoritmo e se é preemptável ou não
ALGORITMOS = [
    (algoritimos.escalonador_fcfs, False),
    (algoritimos.escalonador_sjf, False),
    (algoritimos.escalonador_rr, False),
    (algoritimos.escalonador_priority, False),
    (algoritimos.escalonador_edf, False),
    (algoritimos.escalonador_lottery, False),
    (algoritimos.escalonador_hrrn, False)
]

# Lista de tarefas iniciais
START_TASKS = [
    TarefaCAV("Processo1", chegada=0, duracao=5, prioridade=1, deadline=10),
    TarefaCAV("Processo2", chegada=1, duracao=3, prioridade=2, deadline=8),
    TarefaCAV("Processo3", chegada=2, duracao=2, prioridade=1, deadline=5),
    TarefaCAV("Processo4", chegada=3, duracao=4, prioridade=3, deadline=12),
    TarefaCAV("Processo5", chegada=4, duracao=1, prioridade=2, deadline=6)
]
# Estes valores podem ser ajustados via linha de comando
OVERLOAD_COST = 0.6  # Tempo de sobrecarga
TIME_SLICE = 1 # Tempo entre cada tick do escalonador
# Função para criar tarefas a partir de START_TASKS
# Nescessária para criar novas instâncias de TarefaCAV ao utilizar varios algoritmos
# Caso contrário, todas as instâncias de TarefaCAV seriam as mesmas e portatnto, teriam terminado apos a primeira execução
def create_tasks():
    tasks = []
    for i in range(len(START_TASKS)):
        tasks.append(TarefaCAV(**START_TASKS[i].__dict__))
    return tasks
if __name__ == "__main__":
    # Argumentos de linha de comando
    parser = argparse.ArgumentParser(description="Simulador de Escalonamento de Processos",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", type=float, default=0.5,
                        help="tempo de sleep entre ticks (padrão: 0.5) numeros negativos não são permitidos, 0 desativa o sleep"),
    parser.add_argument("-f", "--file", type=str, default="",
                        help="caminho para o arquivo de entrada")
    parser.add_argument("-o", "--output", type=str, default="",
                        help="caminho para o arquivo de saída (padrão: não salvar) !Cuidado, sobrescreve o arquivo se já existir!")
    parser.add_argument("-c", "--overload_cost", type=float, default=OVERLOAD_COST,
                        help=f"custo de sobrecarga (padrão: {OVERLOAD_COST})")
    parser.add_argument("-ts", "--time-slice", type=float, default=TIME_SLICE,
                        help=f"tempo de slice do escalonador (padrão: {TIME_SLICE})")
    parser.add_argument("-m", "--manual", action='store_true',
                        help="pede input ao usuario a cada algoritmo utilizado.")
    args = parser.parse_args()


    data = [] # Lista para armazenar os dados; resultados das simulações
    
    if args.file:
        args.file = args.file.strip()
        # Basic file validation
        if not os.path.isfile(args.file):
            print(f"Arquivo '{args.file}' não encontrado.")
            quit()
        if not args.file.endswith(".json"):
            print("Arquivo deve ser .json")
            quit()
        # Read tasks from file
        with open(args.file, "r") as f:
            file = json.load(f)
            if "tasks" in file:
                START_TASKS = []
                for t in file["tasks"]:
                    START_TASKS.append(TarefaCAV(**t))
            if "algoritmos" in file:
                ALGORITMOS = []
                for a in file["algoritmos"]:
                    ALGORITMOS.append((getattr(algoritimos, "escalonador_" + a["name"]), a["preemptable"]))
             

    # Desabilita o cursor do console para uma melhor visualização
    console.show_cursor(False)
    
    cav_id = 0
    # Simula cada algoritmo com as tarefas criadas
    for alg, preemptable in ALGORITMOS:
        # Cria uma nova instância de CAV para cada algoritmo
        simulator = Escalonador(alg(), preemptable, time_slice=args.time_slice, sobrecarga=args.overload_cost)
        cav = CAV(cav_id, escalonador=simulator)
        cav_id += 1 # Incrementa o ID do CAV para cada iteração
        for _task in copy.deepcopy(START_TASKS): #cria novas instâncias das tasks iniciais
            cav.adicionar_tarefa(_task)
        
        cav.simular(args.t)
        result = cav.get_statistics()
        data.append((alg.__name__, preemptable, cav.id, result))
        if args.manual:
            input(f"\033[93;1mPressione Enter para continuar com o próximo algoritmo...\033[0m")

        # simulator.start_sync()
        # simulator.print_snapshot()
    if args.output:
        print(f"\033[92;1mSalvando resultados em \033[4m{args.output}\033[0m")
        if not os.path.exists(args.output):
            with open(args.output, "w") as f:
                f.write("")
        else:
            os.remove(args.output)
            with open(args.output, "w") as f:
                f.write("")
  
    for _data in data:
        # console.home()
        str = f"Cav #{_data[2]} Algoritmo: {_data[0]}, Preemptável: {_data[1]} \n"

        str += "\n\t".join(f"{k}: {v}" for k, v in _data[3].items())
        if args.output:
            print(f"\033[92;1mSalvando resultados em \033[4m{args.output}\033[0m")
            with open(args.output, "a") as f:
                f.write(str + "\n")
        print(str)

    console.show_cursor(True)