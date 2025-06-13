import os
import json
import string
from collections import defaultdict, Counter
import re
from nltk.corpus import stopwords
import nltk

# Baixar stopwords caso não tenha
nltk.download('stopwords')

# -------------------
# Configurações gerais
CAMINHO_BASE = "resultados"
PASTA_SAIDA_INDEX = os.path.join(CAMINHO_BASE, "indexacao_saida")
PASTA_SAIDA_EXTRA = os.path.join(CAMINHO_BASE, "extracao_saida")
STOPWORDS = set(stopwords.words('portuguese'))

os.makedirs(PASTA_SAIDA_INDEX, exist_ok=True)
os.makedirs(PASTA_SAIDA_EXTRA, exist_ok=True)

# -------------------
# Funções para indexação textual (tokenização, stopwords, dicionário, índice invertido)

def limpar_token(token):
    token = token.lower()
    token = token.translate(str.maketrans("", "", string.punctuation))
    return token.strip()

def processar_arquivo_indexacao(caminho_arquivo, nome_relativo, dicionario, indice_invertido):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        for i, linha in enumerate(linhas):
            tokens = linha.strip().split()
            tokens = [limpar_token(t) for t in tokens if limpar_token(t) not in STOPWORDS and limpar_token(t)]
            for token in tokens:
                dicionario[token] += 1
                indice_invertido[token].add(f"{nome_relativo}:linha{i+1}")

def gerar_ranking(dicionario, top_n=100):
    linhas = [f"{palavra}: {frequencia}" for palavra, frequencia in dicionario.most_common(top_n)]
    caminho_ranking = os.path.join(PASTA_SAIDA_INDEX, "ranking.txt")
    with open(caminho_ranking, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

def percorrer_arquivos_indexacao(base_path):
    dicionario = Counter()
    indice_invertido = defaultdict(set)

    for campeonato in os.listdir(base_path):
        caminho_campeonato = os.path.join(base_path, campeonato)
        if not os.path.isdir(caminho_campeonato):
            continue

        for time in os.listdir(caminho_campeonato):
            caminho_time = os.path.join(caminho_campeonato, time, "jogadores")
            if not os.path.isdir(caminho_time):
                continue

            for arquivo in os.listdir(caminho_time):
                if arquivo.endswith(".txt"):
                    caminho_arquivo = os.path.join(caminho_time, arquivo)
                    nome_relativo = os.path.join(campeonato, time, "jogadores", arquivo)
                    processar_arquivo_indexacao(caminho_arquivo, nome_relativo, dicionario, indice_invertido)

    # Salvar dicionário
    caminho_dicionario = os.path.join(PASTA_SAIDA_INDEX, "dicionario.json")
    with open(caminho_dicionario, "w", encoding="utf-8") as f:
        json.dump(dicionario, f, indent=2, ensure_ascii=False)

    # Salvar índice invertido (transformar sets em listas)
    indice_invertido_json = {k: list(v) for k, v in indice_invertido.items()}
    caminho_indice = os.path.join(PASTA_SAIDA_INDEX, "indice_invertido.json")
    with open(caminho_indice, "w", encoding="utf-8") as f:
        json.dump(indice_invertido_json, f, indent=2, ensure_ascii=False)

    # Gerar ranking
    gerar_ranking(dicionario)

    print("✔️ Indexação textual concluída!")
    print(f"- Dicionário salvo em: {caminho_dicionario}")
    print(f"- Índice invertido salvo em: {caminho_indice}")
    print(f"- Ranking salvo em: {os.path.join(PASTA_SAIDA_INDEX, 'ranking.txt')}")

# -------------------
# Funções para extração numérica das estatísticas dos arquivos (exemplo simplificado)

def extrair_estatisticas_de_arquivo(caminho_arquivo):
    estatisticas = {}
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        texto = f.read()

    # Expressões regulares para extrair dados numéricos com rótulos
    # Exemplo: "Assistências: 0"
    # Ajuste e acrescente conforme seu padrão de dados
    padrao = re.compile(r'([A-Za-zÀ-ú\s\(\)]+):\s*([\d.,]+)')
    for match in padrao.finditer(texto):
        chave = match.group(1).strip()
        valor = match.group(2).replace(',', '.')  # normaliza vírgula para ponto
        try:
            if '.' in valor:
                valor_num = float(valor)
            else:
                valor_num = int(valor)
            estatisticas[chave] = valor_num
        except:
            # se não conseguir converter, ignora
            pass
    return estatisticas

def percorrer_arquivos_extracao(base_path):
    dados_completos = {}

    for campeonato in os.listdir(base_path):
        caminho_campeonato = os.path.join(base_path, campeonato)
        if not os.path.isdir(caminho_campeonato):
            continue

        dados_completos[campeonato] = {}

        for time in os.listdir(caminho_campeonato):
            caminho_time = os.path.join(caminho_campeonato, time, "jogadores")
            if not os.path.isdir(caminho_time):
                continue

            dados_completos[campeonato][time] = {}

            for arquivo in os.listdir(caminho_time):
                if arquivo.endswith(".txt"):
                    caminho_arquivo = os.path.join(caminho_time, arquivo)
                    nome_jogador = os.path.splitext(arquivo)[0]
                    estatisticas = extrair_estatisticas_de_arquivo(caminho_arquivo)
                    dados_completos[campeonato][time][nome_jogador] = estatisticas

    # Salvar dados extraídos em JSON
    caminho_saida = os.path.join(PASTA_SAIDA_EXTRA, "dados_estatisticas_jogadores.json")
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados_completos, f, indent=2, ensure_ascii=False)

    print("✔️ Extração numérica concluída!")
    print(f"- Dados das estatísticas salvos em: {caminho_saida}")

# -------------------
# Script principal que chama ambos

def main():
    print("🚀 Iniciando extração dos dados numéricos das estatísticas...")
    percorrer_arquivos_extracao(CAMINHO_BASE)
    print()
    print("🚀 Iniciando indexação textual para busca por termos...")
    percorrer_arquivos_indexacao(CAMINHO_BASE)
    print()
    print("🎯 Processo finalizado. Você tem agora:")
    print(f" - Dados numéricos estruturados em JSON dentro de: {PASTA_SAIDA_EXTRA}")
    print(f" - Índice invertido, dicionário e ranking em: {PASTA_SAIDA_INDEX}")

if __name__ == "__main__":
    main()
