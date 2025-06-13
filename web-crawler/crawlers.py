import os
import time
import json
import random
import logging
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Diretórios
HTML_DIR = "html"
CAMPEONATO_DIR = os.path.join(HTML_DIR, "campeonatos")
ESTATISTICAS_JOGADORES_DIR = os.path.join(HTML_DIR, "estatisticas_jogadores")
LOG_PATH = "crawler.log"

# Estatísticas
downloads_realizados = 0
paginas_salvas = 0

# Logging
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
        "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
    })
    return driver

def salvar_html(html, caminho):
    global paginas_salvas
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
        paginas_salvas += 1

def baixar_campeonato_com_abas(driver, nome, ano, url):
    global downloads_realizados
    slug = f"{nome.lower().replace(' ', '-')}-{ano}".replace("/", "-")
    print(f"\n\U0001F3C6 Processando campeonato: {slug}")

    try:
        driver.get(url)
        time.sleep(30)  # Aguarda carregamento inicial
        abas = ["Geral", "Ataque", "Defensores", "Passe", "Guarda-Redes"]

        for aba in abas:
            print(f"\n\U0001F518 Buscando aba: {aba}")
            try:
                botoes = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.px_lg.py_sm button.Chip"))
                )
                clicado = False
                for b in botoes:
                    if aba.lower() == b.text.strip().lower():
                        print(f"➡️ Clicando na aba: {b.text.strip()}")
                        driver.execute_script("arguments[0].click();", b)
                        clicado = True
                        break

                if not clicado:
                    print(f"⚠️ Aba '{aba}' não encontrada.")
                    continue

                time.sleep(30)  # Aguarda carregamento da aba
                pagina = 1
                while True:
                    nome_arquivo = f"{slug}-{aba.lower().replace(' ', '-')}-{pagina}.html"
                    caminho_arquivo = os.path.join(ESTATISTICAS_JOGADORES_DIR, nome_arquivo)
                    salvar_html(driver.page_source, caminho_arquivo)
                    print(f"✔️ Salvou: {nome_arquivo}")
                    downloads_realizados += 1

                    try:
                        proximo = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Próximo']"))
                        )
                        if "disabled" in proximo.get_attribute("class"):
                            break
                        proximo.click()
                        pagina += 1
                        time.sleep(3)
                    except:
                        break

            except Exception as e:
                print(f"⚠️ Erro ao processar aba '{aba}': {e}")

    except Exception as e:
        logging.error(f"❌ Erro ao processar campeonato {slug}: {e}")

def main():
    global downloads_realizados, paginas_salvas
    inicio = time.time()

    with open("campeonatos.json", "r", encoding="utf-8") as f:
        campeonatos = json.load(f)

    driver = iniciar_driver()

    for camp in campeonatos:
        nome = camp["campeonato_nome"]
        ano = camp["campeonato_ano"]
        url = camp["url_campeonato"]
        baixar_campeonato_com_abas(driver, nome, ano, url)

    driver.quit()
    fim = time.time()
    tempo_total = fim - inicio

    print("\n\U0001F4CA Estatísticas de execução:")
    print(f"🔢 Total de páginas visitadas: {downloads_realizados}")
    print(f"📁 Total de arquivos HTML salvos: {paginas_salvas}")
    print(f"⏱️ Tempo total de execução: {str(datetime.fromtimestamp(tempo_total, timezone.utc).strftime('%H:%M:%S'))}")

if __name__ == "__main__":
    main()
