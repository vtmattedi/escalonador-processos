#### Grupo:

* Vitor Mattedi Carvalho
* Gerson Daniel

#### Mudanças Sugeridas:

* Separação de responsabilidades:
  * Modularização do projeto, implmentando cada parte em sseu própio arquivo.
  * A execução das tarefas passa a ser responsabilidade do SO (simluador neste caso) e não do escalonador.
  * Um CAV passa a ter um SO (simulado) que faz o
* Modificar a classe tarefa para incluir:
  * Estado atual (Pronto, Finalizado, Executando)
  * Suporte a deadline
  * Executar e calcular as estatisticas (response time, turnaround time etc)
* O escalonador passa a ser responsavél por:
  * Dado um conjunto de tarefas *t*, ordenar eles para que o SO atribua aos processadores disponiveis
  * Quem dita se o escalonador é preemptivel ou não é o sistema e não o algoritimo utilizado:
    * Nota: tem algoritimos que só fazem sentido com/sem preempção, ficando a cargo do usuario utilizar as configurações corretas.
* Novos algoritimos de escalonamento:
  * Documentar como implementar novos escalonadores neste novo sistema.
  * Adaptar os algoritimos já implementados para o novo sistema (FIFO, RR, PRIORIDADE).
  * Implementar os seguintes algoritimos:
    * SJF
    * EDF
    * LOTERIA JUSTA
    * HRRN

#### Motivações:

* Melhorar a manutenibilidade do codigo e a implementação de novas ferramentas
* Facilitar O uso do software para testes especificos ou varios testes de vez sem ter que modificar codigo.
* Facilitar a implementação de processos com 2 ou mais processadores e, no contexto de CAV, possibilitar que tarefas sejam executas com prioridade por um processador especifico: (uma tarefa quer executar nos processadores de baixo consumo ou de alto consumo ou no processador dedicado ao I/O etc.)
* Estimar as metricas para cada um dos algoritimos testados
