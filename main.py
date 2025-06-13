import os
import time
import json
import random
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import argparse

# Diretórios
HTML_DIR = "html"
CAMPEONATO_DIR = os.path.join(HTML_DIR, "campeonatos")
TIME_DIR = os.path.join(HTML_DIR, "times")
JOGADOR_DIR = os.path.join(HTML_DIR, "jogadores")
EXTRACAO_DIR = "extracao"
LOG_PATH = "crawler.log"

visitadas = 0
salvas = 0

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(message)s")

def iniciar_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """
    })
    return driver

def salvar_html(html, caminho):
    global salvas
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
        salvas += 1

def baixar_html(driver, url, destino):
    global visitadas
    try:
        driver.get(url)
        time.sleep(random.uniform(6, 10))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        salvar_html(driver.page_source, destino)
        visitadas += 1
        logging.info(f"✔️ Sucesso: {url}")
    except Exception as e:
        logging.error(f"❌ Falha: {url} - {e}")

def extrair_links_times(caminho_html):
    with open(caminho_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        return sorted(set("https://www.sofascore.com" + a["href"] for a in soup.find_all("a", href=True) if "/time/futebol/" in a["href"]))

def extrair_links_jogadores(caminho_html):
    with open(caminho_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        return sorted(set("https://www.sofascore.com" + a["href"] for a in soup.find_all("a", href=True) if "/jogador/" in a["href"]))

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
                    dados[spans[0].text.strip()] = spans[1].text.strip()
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
                estatisticas[categoria] = {span[0].text.strip(): span[1].text.strip() for span in [l.find_all("span") for l in linhas] if len(span) == 2}
            except:
                continue
    return estatisticas

def extrair_estatisticas_jogador(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    dados = defaultdict(dict)
    secao_atual = None
    for div in soup.find_all("div", class_="Box Flex dlyXLO bnpRyo"):
        spans = div.find_all("span")
        if len(spans) == 2 and secao_atual:
            dados[secao_atual][spans[0].text.strip()] = spans[1].text.strip()
        elif len(spans) == 1 and spans[0].text.strip() in ["Partidas", "Ataque", "Passe", "Defendendo", "Outros (por partida)", "Cartões"]:
            secao_atual = spans[0].text.strip()
    nota = soup.find("span", class_="sc-himrzO iaYywV")
    if nota:
        dados["Nota Sofascore"] = {"Média": nota.text.strip()}
    return dict(dados)

def main_crawl():
    global visitadas, salvas
    inicio = time.time()
    with open("campeonatos.json", "r", encoding="utf-8") as f:
        campeonatos = json.load(f)
    driver = iniciar_driver()
    for camp in campeonatos:
        nome = camp["campeonato_nome"].lower().replace(" ", "-")
        ano = camp["campeonato_ano"]
        url = camp["url_campeonato"]
        slug = f"{nome}-{ano}"
        print(f"🏆 Baixando campeonato: {slug}")
        baixar_html(driver, url, os.path.join(CAMPEONATO_DIR, f"{slug}.html"))
    urls_times = sorted(set(url for arq in os.listdir(CAMPEONATO_DIR) if arq.endswith(".html") for url in extrair_links_times(os.path.join(CAMPEONATO_DIR, arq))))
    for url in urls_times:
        slug = url.strip("/").split("/")[-2]
        print(f"🏟️ Baixando time: {slug}")
        baixar_html(driver, url, os.path.join(TIME_DIR, f"{slug}.html"))
    urls_jogadores = sorted(set(url for arq in os.listdir(TIME_DIR) if arq.endswith(".html") for url in extrair_links_jogadores(os.path.join(TIME_DIR, arq))))
    for url in urls_jogadores:
        slug = url.strip("/").split("/")[-1]
        print(f"👤 Baixando jogador: {slug}")
        baixar_html(driver, url, os.path.join(JOGADOR_DIR, f"{slug}.html"))
    driver.quit()
    tempo_total = time.time() - inicio
    print("\n📊 Estatísticas do Crawler:")
    print(f"🔢 Total de páginas visitadas: {visitadas}")
    print(f"📁 Total de arquivos HTML salvos: {salvas}")
    print(f"⏱️ Tempo total: {str(datetime.fromtimestamp(tempo_total, timezone.utc).strftime('%H:%M:%S'))}")

def main_extract():
    print("\n📊 Extraindo estatísticas dos campeonatos...")
    for arquivo in os.listdir(CAMPEONATO_DIR):
        if arquivo.endswith(".html"):
            caminho = os.path.join(CAMPEONATO_DIR, arquivo)
            slug = os.path.splitext(arquivo)[0]
            dados = extrair_estatisticas_campeonato(caminho)
            if dados:
                salvar_json(dados, os.path.join(EXTRACAO_DIR, "campeonatos", f"{slug}.json"))
                print(f"✔️ {slug}")
    print("\n🏟️ Extraindo estatísticas dos times...")
    for arquivo in os.listdir(TIME_DIR):
        if arquivo.endswith(".html"):
            caminho = os.path.join(TIME_DIR, arquivo)
            slug = os.path.splitext(arquivo)[0]
            dados = extrair_estatisticas_time(caminho)
            if dados:
                salvar_json(dados, os.path.join(EXTRACAO_DIR, "times", f"{slug}.json"))
                print(f"✔️ {slug}")
    print("\n👤 Extraindo estatísticas dos jogadores...")
    for arquivo in os.listdir(JOGADOR_DIR):
        if arquivo.endswith(".html"):
            caminho = os.path.join(JOGADOR_DIR, arquivo)
            slug = os.path.splitext(arquivo)[0]
            dados = extrair_estatisticas_jogador(caminho)
            if dados:
                salvar_json(dados, os.path.join(EXTRACAO_DIR, "jogadores", f"{slug}.json"))
                print(f"✔️ {slug}")
    print("\n✅ Extração finalizada.")

def main():
    main_crawl()
    main_extract()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawler e Extrator de dados do Sofascore")
    parser.add_argument("--crawl", action="store_true", help="Baixar páginas HTML")
    parser.add_argument("--extract", action="store_true", help="Extrair estatísticas")
    parser.add_argument("--all", action="store_true", help="Executar crawl + extração")
    args = parser.parse_args()

    if args.all:
        main()
    else:
        if args.crawl:
            print("🚀 Executando apenas o CRAWLER")
            main_crawl()
        if args.extract:
            print("🔍 Executando apenas a EXTRAÇÃO")
            main_extract()