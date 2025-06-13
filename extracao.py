import os
import json
from bs4 import BeautifulSoup

# Diretórios de origem e destino
HTML_CAMPEONATO_DIR = "html/campeonatos"
HTML_TIME_DIR = "html/times"
HTML_JOGADOR_DIR = "html/jogadores"
DESTINO_DIR = "resultados_footystats"

os.makedirs(DESTINO_DIR, exist_ok=True)

def salvar_json(dados, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def extrair_estatisticas_campeonato(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    dados = {}
    tabelas = soup.find_all("table")
    for tabela in tabelas:
        headers = [th.get_text(strip=True) for th in tabela.find_all("th")]
        for tr in tabela.find_all("tr"):
            cols = tr.find_all("td")
            if len(cols) >= 2:
                time = cols[0].get_text(strip=True)
                estatisticas = {headers[i]: cols[i].get_text(strip=True) for i in range(1, min(len(headers), len(cols)))}
                dados[time] = estatisticas
    return dados

def extrair_estatisticas_jogador(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    dados = {}
    nome_tag = soup.find("meta", {"itemprop": "name"})
    nome = nome_tag["content"] if nome_tag else "desconhecido"
    dados["nome"] = nome

    role_tag = soup.find("p", itemprop="roleName")
    if role_tag:
        dados["posição"] = role_tag.get_text(strip=True)

    # Busca valor numérico que geralmente representa média de gols ou rating
    valor_tag = soup.find("p", style="font-weight:500;")
    if valor_tag:
        dados["valor"] = valor_tag.get_text(strip=True)

    return dados

def main():
    # Coletar estatísticas dos campeonatos
    for arquivo in os.listdir(HTML_CAMPEONATO_DIR):
        if arquivo.endswith(".html"):
            nome = arquivo.replace(".html", "")
            caminho = os.path.join(HTML_CAMPEONATO_DIR, arquivo)
            print(f"📊 Processando campeonato: {nome}")
            stats = extrair_estatisticas_campeonato(caminho)
            salvar_json(stats, os.path.join(DESTINO_DIR, f"{nome}_campeonato.json"))

    # Coletar estatísticas dos jogadores
    for arquivo in os.listdir(HTML_JOGADOR_DIR):
        if arquivo.endswith(".html"):
            slug = arquivo.replace(".html", "")
            caminho = os.path.join(HTML_JOGADOR_DIR, arquivo)
            print(f"👤 Processando jogador: {slug}")
            stats = extrair_estatisticas_jogador(caminho)
            salvar_json(stats, os.path.join(DESTINO_DIR, "jogadores", f"{slug}.json"))

if __name__ == "__main__":
    main()