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
visitadas = 0
salvas = 0

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
    global salvas
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
        salvas += 1

def baixar_campeonato_com_abas(driver, nome, ano, url):
    global visitadas
    slug = f"{nome.lower().replace(' ', '-')}-{ano}".replace("/", "-")
    print(f"🏆 Processando campeonato: {slug}")
    
    try:
        driver.get(url)
        print("⏳ Aguardando 30 segundos antes de iniciar cliques...")
        time.sleep(30)  # Espera inicial maior
        abas = ["Geral", "Ataque", "Defensores", "Passe", "Guarda-Redes"]

        for aba in abas:
            try:
                print(f"🔘 Clicando na aba: {aba}")
                botao_aba = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{aba}']"))
                )
                botao_aba.click()
                
                print(f"⏳ Aguardando 30 segundos para carregar conteúdo da aba {aba}...")
                time.sleep(30)  # Espera após clique
                
                pagina = 1
                while True:
                    nome_arquivo = f"{slug}-{aba.lower().replace(' ', '-')}-{pagina}.html"
                    caminho_arquivo = os.path.join(ESTATISTICAS_JOGADORES_DIR, nome_arquivo)
                    salvar_html(driver.page_source, caminho_arquivo)
                    print(f"✔️ Salvou: {nome_arquivo}")
                    visitadas += 1

                    # Verifica se há botão "Próximo"
                    try:
                        proximo = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Próximo']"))
                        )
                        if "disabled" in proximo.get_attribute("class"):
                            break
                        proximo.click()
                        pagina += 1
                        time.sleep(2)
                    except:
                        break

            except Exception as e:
                print(f"⚠️ Não foi possível clicar na aba {aba}: {e}")

    except Exception as e:
        logging.error(f"❌ Erro ao processar campeonato {slug}: {e}")


def main():
    global visitadas, salvas
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

    print("\n📊 Estatísticas de execução:")
    print(f"🔢 Total de páginas visitadas: {visitadas}")
    print(f"📁 Total de arquivos HTML salvos: {salvas}")
    print(f"⏱️ Tempo total de execução: {str(datetime.fromtimestamp(tempo_total, timezone.utc).strftime('%H:%M:%S'))}")

if __name__ == "__main__":
    main()