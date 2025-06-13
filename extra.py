import os
import json
from bs4 import BeautifulSoup

HTML_DIR = "html"
EXTRACAO_DIR = "extracao"

def salvar_json(dados, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def extrair_estatisticas_campeonato(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    dados = {}
    container = soup.find("span", string="estatísticas")
    if container:
        pai = container.find_parent("div", class_="bg_surface.s2")
        if pai:
            linhas = pai.find_all("div", class_="d_flex ai_center jc_space-between py_sm mdDown:px_sm md:px_lg")
            for linha in linhas:
                spans = linha.find_all("span", class_="textStyle_body.medium c_neutrals.nLv1")
                if len(spans) == 2:
                    chave = spans[0].text.strip()
                    valor = spans[1].text.strip()
                    dados[chave] = valor
    return dados

def extrair_estatisticas_time(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    estatisticas = {}
    categorias = ["Geral", "Ataque", "Precisão de passe", "Defendendo", "Diversos"]
    for categoria in categorias:
        secao = soup.find("span", string=categoria)
        if secao:
            try:
                box = secao.find_parent("button").find_next("div")
                linhas = box.find_all("div", class_="Box Flex dlyXLO bnpRyo")
                estatisticas[categoria] = {}
                for linha in linhas:
                    spans = linha.find_all("span")
                    if len(spans) == 2:
                        chave = spans[0].text.strip()
                        valor = spans[1].text.strip()
                        estatisticas[categoria][chave] = valor
            except:
                continue
    return estatisticas

def extrair_estatisticas_jogador(html_path):
    from collections import defaultdict
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    dados = defaultdict(dict)

    # Nome do jogador
    h1 = soup.find("h1")
    nome_jogador = h1.text.strip() if h1 else "Desconhecido"
    dados["Jogador"] = nome_jogador

    # Time e contrato
    time_info = soup.find("span", string=lambda text: text and "Contrato até" in text)
    if time_info:
        texto = time_info.text.strip()
        partes = texto.split("Contrato até")
        if len(partes) == 2:
            dados["Time"] = partes[0].strip()
            dados["Contrato"] = "Contrato até " + partes[1].strip()
        else:
            dados["Time"] = texto
            dados["Contrato"] = "Desconhecido"
    else:
        dados["Time"] = "Desconhecido"
        dados["Contrato"] = "Desconhecido"

    # Estatísticas organizadas por seções
    secao_atual = None
    for div in soup.find_all("div", class_="Box Flex dlyXLO bnpRyo"):
        spans = div.find_all("span")
        if len(spans) == 2:
            chave = spans[0].text.strip()
            valor = spans[1].text.strip()
            if secao_atual:
                dados[secao_atual][chave] = valor
        elif len(spans) == 1 and spans[0].text.strip() in ["Partidas", "Ataque", "Passe", "Defendendo", "Outros (por partida)", "Cartões"]:
            secao_atual = spans[0].text.strip()

    # Nota Sofascore
    nota = soup.find("span", class_="sc-himrzO iaYywV")
    if nota:
        dados["Nota Sofascore"] = {"Média": nota.text.strip()}

    return dict(dados)

def main():
    # Campeonatos
    print("\n📊 Extraindo estatísticas dos campeonatos...")
    for arquivo in os.listdir(os.path.join(HTML_DIR, "campeonatos")):
        if arquivo.endswith(".html"):
            caminho = os.path.join(HTML_DIR, "campeonatos", arquivo)
            slug = os.path.splitext(arquivo)[0]
            dados = extrair_estatisticas_campeonato(caminho)
            if dados:
                salvar_json(dados, os.path.join(EXTRACAO_DIR, "campeonatos", f"{slug}.json"))
                print(f"✔️ {slug}")

    # Times
    print("\n🏟️ Extraindo estatísticas dos times...")
    for arquivo in os.listdir(os.path.join(HTML_DIR, "times")):
        if arquivo.endswith(".html"):
            caminho = os.path.join(HTML_DIR, "times", arquivo)
            slug = os.path.splitext(arquivo)[0]
            dados = extrair_estatisticas_time(caminho)
            if dados:
                salvar_json(dados, os.path.join(EXTRACAO_DIR, "times", f"{slug}.json"))
                print(f"✔️ {slug}")

    # Jogadores
    print("\n👤 Extraindo estatísticas dos jogadores...")
    for arquivo in os.listdir(os.path.join(HTML_DIR, "jogadores")):
        if arquivo.endswith(".html"):
            caminho = os.path.join(HTML_DIR, "jogadores", arquivo)
            slug = os.path.splitext(arquivo)[0]
            dados = extrair_estatisticas_jogador(caminho)
            if dados:
                salvar_json(dados, os.path.join(EXTRACAO_DIR, "jogadores", f"{slug}.json"))
                print(f"✔️ {slug}")

    print("\n✅ Extração finalizada.")

if __name__ == "__main__":
    main()