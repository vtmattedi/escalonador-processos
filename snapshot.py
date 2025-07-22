import copy
class snapshot:
    def __init__(self, processos, tempo, algoritimo=None, preemptable=None, at_overload=False):
        self.algoritimo = algoritimo
        self.preemptable = preemptable
        self.processos = copy.deepcopy(processos)
        self.tempo = tempo
        self.at_overload = at_overload