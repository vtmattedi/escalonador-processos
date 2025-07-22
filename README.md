## Trabalho de SO 2025.1

### Simulador de escalonador

#### Pré-Requisitos:

* Pyhton (testado no 3.11)

#### Uso:

* `python3 main.py [-h] [-t T] [-f FILE] [-o OUTPUT] [-c CONTEXT_COST] [-ts TIME_SLICE]`
* `-t`: `tempo de sleep entre ticks (padrão: 0.5) numeros negativos não são permitidos, 0 desativa o sleep (default: 0.5)`.
* `-f`: `arquivo de entrada, com tasks para serem testadas e/ou algoritimos`.
* `-o`: `imprime o resultado final no arquivo de saida escolhido`
* `-c`: `custo para troca de contexto (default: 0.6)`
* `-ts`: `time slice: tempo de execução de uma tarefa selecionada pelo escalonador.`

#### Utilizando arquivo .json

Ao utilizar um arquivo .json ao inves de modificar o main.py para simular diferentes algoritimos e/ou tasks. o arquivo json deve conter um objeto no padrão json com as seguintes chaves:

* "algoritimos":[{"name":string, "preemptable": boolean}, ...]
* "tasks": [{"nome": string, "chegada": int, "duracao": int, "deadline": int, "prioridade": int}, ...]
  Notas:

0. ~algoritimos tem chaves em ingles porque eu não gostei de preemptivel~
1. tanto `name` quanto `preemptable` são nescessarias nos algoritimos
2. Caso um arquivo seja lido que não contem um json valido, o programa encerra-rá.
3. Caso uma das chaves não esteja presente o valor padrão utilizado em `main.py` será utilizando, então, por exemplo passa um json com um objeto vazio não afterá a simulação e também o usuario pode utilizar o json para controlar apenas tasks ou apenas algoritimos.
4. Em tasks, `nome`, `chegada` e `duracao` são obrigatorio mas `deadline` e `prioridade` podem estar ausente em uma ou mais tasks. Elas caem no default `infinito` e `0` respectivamente.
5. o arquivo example.json està disponivel para servir de base.
