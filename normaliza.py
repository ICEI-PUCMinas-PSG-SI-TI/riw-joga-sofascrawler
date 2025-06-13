import os
import json
import re
from collections import defaultdict

# Caminhos
BASE_PATH = "resultados"
SAIDA_CAMPEONATOS = "estatisticas_campeonatos.json"
SAIDA_TIMES = "estatisticas_times.json"
SAIDA_JOGADORES = "estatisticas_jogadores.json"

# Normaliza nomes de chaves para snake_case
def normalizar_chave(chave):
    chave = chave.lower()
    chave = re.sub(r"[^\w\s]", "", chave)
    chave = chave.strip().replace(" ", "_")
    return chave

# Extrai estatísticas de um texto em formato "Chave: valor"
def extrair_estatisticas(texto):
    stats = {}
    linhas = texto.split("\n")
    for linha in linhas:
        if ":" not in linha:
            continue
        partes = linha.split(":", 1)
        chave = normalizar_chave(partes[0])
        valor_raw = partes[1].strip().replace(",", ".")
        try:
            if "%" in valor_raw:
                valor = round(float(valor_raw.replace("%", "")) / 100, 4)
            elif "(" in valor_raw:
                valor = float(re.findall(r"[\d.]+", valor_raw)[0])
            else:
                valor = float(valor_raw) if "." in valor_raw else int(valor_raw)
            stats[chave] = valor
        except:
            continue
    return stats

# Dicionários finais
dados_campeonatos = {}
dados_times = defaultdict(dict)
dados_jogadores = defaultdict(lambda: defaultdict(dict))

# Loop principal
for campeonato in os.listdir(BASE_PATH):
    path_camp = os.path.join(BASE_PATH, campeonato)
    if not os.path.isdir(path_camp):
        continue

    print(f"📁 Lendo campeonato: {campeonato}")

    # ✅ Lê todos os arquivos .txt na raiz do campeonato e acumula num só dicionário
    estatisticas_gerais = {}
    arquivos_raiz = [
        arq for arq in os.listdir(path_camp)
        if os.path.isfile(os.path.join(path_camp, arq)) and arq in ["info_campeonato.txt", "estatisticas.txt", "info.txt"]
    ]

    for arquivo in arquivos_raiz:
        caminho = os.path.join(path_camp, arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            stats = extrair_estatisticas(f.read())
            estatisticas_gerais.update(stats)

    if estatisticas_gerais:
        dados_campeonatos[campeonato] = estatisticas_gerais

    # Times e jogadores
    for time in os.listdir(path_camp):
        path_time = os.path.join(path_camp, time)
        if not os.path.isdir(path_time):
            continue

        # Estatísticas do time
        path_info_time = os.path.join(path_time, "info_time.txt")
        if os.path.isfile(path_info_time):
            with open(path_info_time, "r", encoding="utf-8") as f:
                stats = extrair_estatisticas(f.read())
                dados_times[campeonato][time] = stats

        # Estatísticas dos jogadores
        path_jogadores = os.path.join(path_time, "jogadores")
        if os.path.isdir(path_jogadores):
            for arquivo in os.listdir(path_jogadores):
                if not arquivo.endswith(".txt"):
                    continue
                caminho_jogador = os.path.join(path_jogadores, arquivo)
                nome_jogador = os.path.splitext(arquivo)[0]
                with open(caminho_jogador, "r", encoding="utf-8") as f:
                    stats = extrair_estatisticas(f.read())
                    dados_jogadores[campeonato][time][nome_jogador] = stats

# Salvando os arquivos
with open(SAIDA_CAMPEONATOS, "w", encoding="utf-8") as f:
    json.dump(dados_campeonatos, f, indent=2, ensure_ascii=False)

with open(SAIDA_TIMES, "w", encoding="utf-8") as f:
    json.dump(dados_times, f, indent=2, ensure_ascii=False)

with open(SAIDA_JOGADORES, "w", encoding="utf-8") as f:
    json.dump(dados_jogadores, f, indent=2, ensure_ascii=False)

# ✅ Diagnóstico final
print("\n✅ Extração finalizada com sucesso!")
print(f"🏆 Campeonatos extraídos: {len(dados_campeonatos)}")
print(f"🏟️ Times extraídos: {sum(len(t) for t in dados_times.values())}")
print(f"👥 Jogadores extraídos: {sum(len(j) for c in dados_jogadores.values() for j in c.values())}")