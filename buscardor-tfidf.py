import os
import json
import math
from collections import Counter

# Caminhos
BASE_PATH = "resultados"
INDEX_PATH = os.path.join(BASE_PATH, "indexacao_saida")
DICT_PATH = os.path.join(INDEX_PATH, "dicionario.json")

# Carregar dicionário
with open(DICT_PATH, "r", encoding="utf-8") as f:
    dicionario = json.load(f)

# Contar total de documentos (arquivos de jogadores)
def contar_arquivos_jogadores():
    total = 0
    for campeonato in os.listdir(BASE_PATH):
        path_camp = os.path.join(BASE_PATH, campeonato)
        if not os.path.isdir(path_camp):
            continue
        for time in os.listdir(path_camp):
            path_jogadores = os.path.join(path_camp, time, "jogadores")
            if os.path.isdir(path_jogadores):
                total += len([arq for arq in os.listdir(path_jogadores) if arq.endswith(".txt")])
    return total

TOTAL_DOCS = contar_arquivos_jogadores()

def tokenizar(texto):
    return [palavra.strip(".,:;%").lower() for palavra in texto.split()]

def calcular_tfidf_documentos():
    tfidf_docs = {}
    for campeonato in os.listdir(BASE_PATH):
        path_camp = os.path.join(BASE_PATH, campeonato)
        if not os.path.isdir(path_camp):
            continue

        for time in os.listdir(path_camp):
            path_jogadores = os.path.join(path_camp, time, "jogadores")
            if not os.path.isdir(path_jogadores):
                continue

            for arquivo in os.listdir(path_jogadores):
                if not arquivo.endswith(".txt"):
                    continue

                path_arquivo = os.path.join(path_jogadores, arquivo)
                print(f"✔️ Lendo: {campeonato}/{time}/{arquivo}")
                with open(path_arquivo, "r", encoding="utf-8") as f:
                    texto = f.read()
                tokens = tokenizar(texto)
                tf = Counter(tokens)
                doc_tfidf = {}
                for termo, freq in tf.items():
                    df = dicionario.get(termo, 1)
                    idf = math.log(TOTAL_DOCS / df)
                    doc_tfidf[termo] = freq * idf
                nome_doc = os.path.join(campeonato, time, "jogadores", arquivo)
                tfidf_docs[nome_doc] = doc_tfidf
    print(f"\n📄 Total de documentos TF-IDF carregados: {len(tfidf_docs)}\n")
    return tfidf_docs

def calcular_similaridade(v1, v2):
    termos = set(v1.keys()) | set(v2.keys())
    dot = sum(v1.get(t, 0) * v2.get(t, 0) for t in termos)
    norm1 = math.sqrt(sum(v ** 2 for v in v1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in v2.values()))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0

def buscar(consulta, tfidf_docs):
    tokens = tokenizar(consulta)
    tf = Counter(tokens)
    consulta_tfidf = {}
    for termo, freq in tf.items():
        df = dicionario.get(termo, 1)
        idf = math.log(TOTAL_DOCS / df)
        consulta_tfidf[termo] = freq * idf

    ranking = []
    for doc, vetor in tfidf_docs.items():
        score = calcular_similaridade(consulta_tfidf, vetor)
        if score > 0:
            ranking.append((doc, score))

    return sorted(ranking, key=lambda x: x[1], reverse=True)

# EXECUÇÃO
if __name__ == "__main__":
    tfidf_docs = calcular_tfidf_documentos()
    print("🔍 Buscador pronto (digite 'sair' para encerrar)\n")

    while True:
        consulta = input("Consulta: ").strip().lower()
        if consulta == "sair":
            break
        resultados = buscar(consulta, tfidf_docs)
        if resultados:
            print(f"\n📊 Resultados para '{consulta}':\n")
            for i, (doc, score) in enumerate(resultados[:10], 1):
                print(f"{i}. {doc}  [score: {score:.4f}]")
        else:
            print("⚠️ Nenhum resultado relevante encontrado.\n")
