import sys
import os
import subprocess
import time

# ==============================================================================
# CONFIGURAÇÃO DA COMPETIÇÃO (Modifique apenas este dicionário para outros eventos)
# ==============================================================================
# Configuração do comportamento do INPUT e do OUTPUT para cada problema:
# - "linhas_fixas": Ocupa sempre a quantidade exata de linhas definida.
#    - "input/output_linhas": Quantidade de linhas
#
# - "matriz_dinamica": O tamanho é calculado com base em um número do cabeçalho.
#    - "input/output_indice_m": Posição do número que determina as linhas do input.
#    - "input/output_linhas_extras": Quantidade de linhas após as M linhas

CONFIG_PROBLEMAS = {
    "p1": {
        "pontos": 20,
        "input_modo": "linhas_fixas",   "input_linhas": 1, # Ex: L,D e K,P
        "output_modo": "linhas_fixas",  "output_linhas": 1 # 1 linha de resposta
    },
    "p2": {
        "pontos": 30,
        "input_modo": "matriz_dinamica",   
        "input_indice_m": 0, 
        "input_linhas_extras": 0,

        "output_modo": "linhas_fixas",  "output_linhas": 1 # 1 linha de resposta
    },
    "p3": {
        "pontos": 50,
        # Ex: Robô no labirinto M x N com C comandos
        "input_modo": "matriz_dinamica",
        "input_indice_m": 0,       # O número M está na posição 0 da primeira linha
        "input_linhas_extras": 1,   # 1 linha de comandos após a matriz
        
        # Se o output do problema difícil exiba a matriz final modificada:
        "output_modo": "linhas_fixas", "output_linhas": 1  # Apenas as M linhas da matriz, sem extras
    }
}

TIMEOUT_EXECUCAO = 2.0  # Tempo limite por teste (em segundos)
# ==============================================================================

COR_VERDE = "\033[92m"
COR_VERMELHO = "\033[91m"
COR_RESET = "\033[0m"

def separar_casos_teste(id_problema, linhas_input, linhas_output):
    """Fatia os arquivos únicos de input e output dinamicamente em pares isolados."""
    if id_problema not in CONFIG_PROBLEMAS:
        return []

    config = CONFIG_PROBLEMAS[id_problema]
    casos = []
    idx_in = 0
    idx_out = 0

    while idx_in < len(linhas_input):
        if not linhas_input[idx_in].strip():
            idx_in += 1
            continue

        try:
            # 1. PROCESSAMENTO DINÂMICO DO INPUT
            valores_cabecalho = linhas_input[idx_in].split()
            
            if config["input_modo"] == "linhas_fixas":
                t_in = config["input_linhas"]
                bloco_in = "\n".join(linhas_input[idx_in : idx_in + t_in])
                idx_in += t_in
                
            elif config["input_modo"] == "matriz_dinamica":
                m_linhas_in = int(valores_cabecalho[config["input_indice_m"]])
                t_in = 1 + m_linhas_in + config["input_linhas_extras"]
                bloco_in = "\n".join(linhas_input[idx_in : idx_in + t_in])
                idx_in += t_in

            # 2. PROCESSAMENTO DINÂMICO DO OUTPUT
            if config["output_modo"] == "linhas_fixas":
                t_out = config["output_linhas"]
                bloco_out = "\n".join(linhas_output[idx_out : idx_out + t_out])
                idx_out += t_out
                
            elif config["output_modo"] == "matriz_dinamica":
                m_linhas_out = int(valores_cabecalho[config["output_indice_m"]])
                t_out = m_linhas_out + config["output_linhas_extras"]
                bloco_out = "\n".join(linhas_output[idx_out : idx_out + t_out])
                idx_out += t_out

            casos.append({
                "input": bloco_in.strip(),
                "esperado": bloco_out.strip()
            })

        except (IndexError, ValueError):
            break

    return casos

def executar_check():
    if len(sys.argv) < 3:
        print(f"{COR_VERMELHO}Erro: Argumentos insuficientes.{COR_RESET}")
        print("Uso correto: python check.py <caminho_do_arquivo.c> <p1|p2|p3>")
        sys.exit(1)

    caminho_c = sys.argv[1]
    id_problema = sys.argv[2].lower()

    if id_problema not in CONFIG_PROBLEMAS:
        print(f"{COR_VERMELHO}Erro: O problema '{id_problema}' não está configurado.{COR_RESET}")
        sys.exit(1)

    if not os.path.exists(caminho_c):
        print(f"{COR_VERMELHO}Erro: O arquivo '{caminho_c}' não foi encontrado.{COR_RESET}")
        sys.exit(1)

    pasta_problema = id_problema
    caminho_input_txt = os.path.join(pasta_problema, "input.txt")
    caminho_output_txt = os.path.join(pasta_problema, "output.txt")

    if not os.path.exists(caminho_input_txt) or not os.path.exists(caminho_output_txt):
        print(f"{COR_VERMELHO}Erro: input.txt ou output.txt ausentes na pasta '{pasta_problema}'.{COR_RESET}")
        sys.exit(1)

    with open(caminho_input_txt, 'r', encoding='utf-8') as f:
        linhas_input = [l.strip() for linha in f.readlines() if (l := linha.strip())]  # noqa: E741
    with open(caminho_output_txt, 'r', encoding='utf-8') as f:
        linhas_output = [l.strip() for linha in f.readlines() if (l := linha.strip())]  # noqa: E741

    casos_teste = separar_casos_teste(id_problema, linhas_input, linhas_output)

    arquivo_executavel = "./programa_aluno.out"
    if os.name == 'nt':
        arquivo_executavel = "programa_aluno.exe"

    print(f"Compilando {caminho_c}...")
    compilacao = subprocess.run(
        ["gcc", caminho_c, "-o", arquivo_executavel],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if compilacao.returncode != 0:
        print(f"{COR_VERMELHO}Erro de Compilação!{COR_RESET}")
        print(compilacao.stderr)
        sys.exit(1)

    erros = []
    tempo_maximo = 0.0
    passou_em_todos = True

    for idx, caso in enumerate(casos_teste, 1):
        tempo_inicio = time.time()
        try:
            processo = subprocess.run(
                [arquivo_executavel],
                input=caso["input"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=TIMEOUT_EXECUCAO
            )
            tempo_fim = time.time()
            tempo_decorrido = tempo_fim - tempo_inicio
            tempo_maximo = max(tempo_maximo, tempo_decorrido)
            
            conteudo_obtido = processo.stdout.strip()
        except subprocess.TimeoutExpired:
            passou_em_todos = False
            erros.append({
                "num": idx, 
                "input": caso["input"], 
                "esperado": caso["esperado"],
                "obtido": f"Tempo limite excedido (Limite: {TIMEOUT_EXECUCAO}s)"
            })
            continue

        if conteudo_obtido != caso["esperado"]:
            passou_em_todos = False
            erros.append({
                "num": idx, "input": caso["input"],
                "esperado": caso["esperado"], "obtido": conteudo_obtido if conteudo_obtido else "[SEM RETORNO]"
            })

    if os.path.exists(arquivo_executavel):
        os.remove(arquivo_executavel)

    print("\n" + "="*40)
    if passou_em_todos:
        print(f"{COR_VERDE}▶ PARABÉNS! O ALUNO PASSOU EM TODOS OS {len(casos_teste)} TESTES! +{CONFIG_PROBLEMAS[id_problema]['pontos']} pontos!{COR_RESET}")
        print(f"Tempo de execução do teste mais lento: {tempo_maximo:.4f} segundos.")
    else:
        print(f"{COR_VERMELHO}▶ O ALUNO NÃO PASSOU.{COR_RESET}")
        print(f"Falhou em {len(erros)} de {len(casos_teste)} casos de teste.\n")
        
        for erro in erros:
            print(f"--- FALHA NO CASO DE TESTE {erro['num']} ---")
            print(f"{COR_VERDE}[INPUT ENVIADO]:{COR_RESET}\n{erro['input']}\n")
            print(f"{COR_VERDE}[OUTPUT ESPERADO]:{COR_RESET}\n{erro['esperado']}\n")
            print(f"{COR_VERMELHO}[OUTPUT DO ALUNO]:{COR_RESET}\n{erro['obtido']}")
            print("-" * 30 + "\n")
    print("="*40)

if __name__ == "__main__":
    executar_check()