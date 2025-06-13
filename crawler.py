import os
import time
import json
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# Diretórios
HTML_DIR = "html"
CAMPEONATO_DIR = os.path.join(HTML_DIR, "campeonatos")
TIME_DIR = os.path.join(HTML_DIR, "times")
JOGADOR_DIR = os.path.join(HTML_DIR, "jogadores")
LOG_PATH = "crawler.log"

# Estatísticas globais
visitadas = 0
salvas = 0

# Logger
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(message)s')

def iniciar_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
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
        time.sleep(random.uniform(5, 8))
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
        times = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            if "/club/" in href or "/clubs/" in href:
                full_url = "https://footystats.org" + href
                times.append(full_url)
        times = sorted(set(times))
        if times:
            print("🔗 Times encontrados na página:")
            for t in times:
                print(" -", t)
        else:
            print("⚠️ Nenhum time encontrado na tabela.")
        return times

def extrair_links_jogadores(caminho_html):
    with open(caminho_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        jogadores = []
        for a in soup.find_all("a", class_="semi-bold", href=True):
            if "/players/" in a["href"]:
                full_url = "https://footystats.org" + a["href"]
                jogadores.append(full_url)
        jogadores = sorted(set(jogadores))
        if jogadores:
            print(f"👤 Jogadores encontrados: {len(jogadores)}")
        else:
            print("⚠️ Nenhum jogador encontrado.")
        return jogadores

def main():
    global visitadas, salvas
    inicio = time.time()

    with open("campeonatos_footystats.json", "r", encoding="utf-8") as f:
        campeonatos = json.load(f)

    driver = iniciar_driver()

    for camp in campeonatos:
        nome = camp["campeonato_nome"].lower().replace(" ", "-")
        ano = camp["campeonato_ano"]
        url = camp["url_campeonato"]
        path = os.path.join(CAMPEONATO_DIR, f"{nome}-{ano}.html")
        print(f"🏆 Baixando campeonato: {nome}-{ano}")
        baixar_html(driver, url, path)

    urls_times = []
    for arquivo in os.listdir(CAMPEONATO_DIR):
        if arquivo.endswith(".html"):
            caminho = os.path.join(CAMPEONATO_DIR, arquivo)
            urls_times.extend(extrair_links_times(caminho))
    urls_times = sorted(set(urls_times))

    for url in urls_times:
        slug = url.strip("/").split("/")[-1]
        path = os.path.join(TIME_DIR, f"{slug}.html")
        print(f"🏟️ Baixando time: {slug}")
        baixar_html(driver, url, path)

    urls_jogadores = []
    for arquivo in os.listdir(TIME_DIR):
        if arquivo.endswith(".html"):
            caminho = os.path.join(TIME_DIR, arquivo)
            urls_jogadores.extend(extrair_links_jogadores(caminho))
    urls_jogadores = sorted(set(urls_jogadores))

    for url in urls_jogadores:
        slug = url.strip("/").split("/")[-1]
        path = os.path.join(JOGADOR_DIR, f"{slug}.html")
        print(f"👤 Baixando jogador: {slug}")
        baixar_html(driver, url, path)

    driver.quit()
    fim = time.time()
    tempo_total = fim - inicio
    print("\n📊 Estatísticas de execução:")
    print(f"🔢 Total de páginas visitadas: {visitadas}")
    print(f"📁 Total de arquivos HTML salvos: {salvas}")
    print(f"⏱️ Tempo total de execução: {str(datetime.fromtimestamp(tempo_total, timezone.utc).strftime('%H:%M:%S'))}")

if __name__ == "__main__":
    main()