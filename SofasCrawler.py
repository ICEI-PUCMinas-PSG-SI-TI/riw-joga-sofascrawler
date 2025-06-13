import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Variável global para contar o número total de arquivos criados
total_arquivos_criados = 0

def iniciar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def salvar_dados(dados, caminho, formato="txt"):

    global total_arquivos_criados

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    
    with open(caminho, "w", encoding="utf-8") as f:
        if isinstance(dados, dict):
            # Se for dicionário de seções (aninhado)
            is_nested = any(isinstance(v, dict) for v in dados.values())
            if is_nested:
                for secao, estatisticas in dados.items():
                    f.write(f"[{secao}]\n")
                    for k, v in estatisticas.items():
                        f.write(f"{k}: {v}\n")
                    f.write("\n")
            else:
                for k, v in dados.items():
                    f.write(f"{k}: {v}\n")
        elif isinstance(dados, str):
            f.write(dados)
        else:
            print(f"⚠️ Tipo de dados inesperado: {type(dados)}")
    total_arquivos_criados += 1

def extrair_tabela_geral_jogadores(driver):
    try:
        tab_button = driver.find_element(By.XPATH, "//a[contains(@href, '/estatisticas-jogadores')]")
        tab_button.click()
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        tabela = soup.find("table")
        dados = {}
        if tabela:
            headers = [th.text.strip() for th in tabela.find_all("th")]
            for row in tabela.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) == len(headers):
                    jogador = cols[0].text.strip()
                    dados[jogador] = {
                        headers[i]: cols[i].text.strip() for i in range(1, len(headers))
                    }
        return dados
    except:
        return {}

def extrair_urls_times(driver, url_campeonato):
    driver.get(url_campeonato)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Find the table containing the standings
    # Based on previous browser_view, the table is likely within a div with class 'sc-hLBwJm gLqgJp' or similar
    # Let's try to find the table directly if possible, or a parent div that contains the standings.
    # The table itself doesn't have a unique ID or class that's easily identifiable from the provided HTML snippets.
    # However, the team links are within <a> tags that are children of <td> elements in the table rows.
    # Let's look for <a> tags that have an href containing '/team/football/' and are within a table.
    
    urls = []
    # Find all <a> tags with href attribute containing '/team/football/'
    team_links = soup.find_all("a", href=lambda href: href and "/team/football/" in href)
    
    for link_tag in team_links:
        href = link_tag["href"]
        url_completa = "https://www.sofascore.com" + href
        if url_completa not in urls:
            urls.append(url_completa)
    return urls

def extrair_estatisticas_time(html):
    soup = BeautifulSoup(html, "html.parser")
    estatisticas = {}
    categorias = ["Geral", "Ataque", "Precisão de passe", "Defendendo", "Diversos"]
    for categoria in categorias:
        span = soup.find("span", string=categoria)
        if not span:
            continue
        try:
            box = span.find_parent("button").find_next("div")
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

def selecionar_visualizacao_lista(driver):
    try:
        opcao_lista = driver.find_element(By.XPATH, "//label[contains(@for, 'listTeamPlayers-')]")
        opcao_lista.click()
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ Erro ao mudar para lista: {e}")

def extrair_jogadores(driver):
    selecionar_visualizacao_lista(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    jogadores = []
    tabela = soup.find("table", class_="Table fEUhaC")
    if tabela:
        linhas = tabela.find_all("tr", class_="TableRow ygnhC")
        for linha in linhas:
            try:
                link_tag = linha.find("a", href=True)
                nome = link_tag.text.strip() if link_tag else "Desconhecido"
                link = "https://www.sofascore.com" + link_tag["href"] if link_tag else ""
                posicao = linha.find("span", class_="Text").text.strip()
                idade = linha.find("div", class_="Text gQjAEx").text.strip()

                # Attempt to extract jersey number
                # The jersey number is usually in a <span> with class 'Cell-number' or similar, or directly in a <td>
                # We need to inspect the HTML to find the correct selector.
                # Based on the image, the number is directly in a <td> element, not a span with class 'Cell-number'
                # Let's try to find the <td> that contains the number.
                # Assuming the number is in the first <td> after the player's name/link, or a specific class.
                # From the image, it looks like the number is in a <td> element with a specific class.
                # Let's try to find a <td> with class 'Cell-number' or similar, or just the first <td> after the name.
                # For now, let's assume it's the first <td> with a numeric value after the player's name.
                # This needs to be verified by inspecting the actual HTML of a player list page.
                numero_camisa_tag = linha.find("td", class_="Cell-number") # This is a placeholder, needs verification
                if not numero_camisa_tag:
                    # If not found with Cell-number, try to find the first td that contains only numbers
                    all_tds = linha.find_all("td")
                    for td in all_tds:
                        if td.text.strip().isdigit():
                            numero_camisa_tag = td
                            break

                numero_camisa = numero_camisa_tag.text.strip() if numero_camisa_tag else "N/A"

                jogadores.append({"nome": nome, "posição": posicao, "idade": idade, "link": link, "numero_camisa": numero_camisa})
            except Exception as e:
                print(f"Erro ao extrair jogador: {e}")
                continue
    return jogadores

def extrair_estatisticas_jogador(driver, url_jogador, campeonato_nome):
    driver.get(url_jogador)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    dados = {}
    categorias = ["Partidas", "Ataque", "Passe", "Defendendo", "Outros (por partida)", "Cartões"]
    for categoria in categorias:
        secao = soup.find("span", string=categoria)
        if not secao:
            continue
        try:
            box = secao.find_parent("button").find_next("div")
            linhas = box.find_all("div", class_="Box Flex dlyXLO bnpRyo")
            dados[categoria] = {}
            for linha in linhas:
                spans = linha.find_all("span")
                if len(spans) == 2:
                    chave = spans[0].text.strip()
                    valor = spans[1].text.strip()
                    dados[categoria][chave] = valor
        except:
            continue
    nota = soup.find("span", class_="sc-himrzO iaYywV")
    if nota:
        dados["Nota Sofascore"] = {"Média": nota.text.strip()}
    return dados

def coletar_dados_time(driver, url_time, campeonato_nome, campeonato_ano, formato="txt"):
    driver.get(url_time)
    time.sleep(3)
    nome_time = url_time.strip("/").split("/")[-2].lower().replace(" ", "-")
    pasta_time = os.path.join("resultados", f"{campeonato_nome.lower().replace(' ', '-')}-{campeonato_ano}", nome_time)
    estatisticas = extrair_estatisticas_time(driver.page_source)
    salvar_dados(estatisticas, os.path.join(pasta_time, "info_time." + formato), formato)
    jogadores = extrair_jogadores(driver)
    for jogador in jogadores:
        print(f"   👤 Coletando jogador: {jogador['nome']} (Camisa: {jogador['numero_camisa']})")
        try:
            stats = extrair_estatisticas_jogador(driver, jogador["link"], campeonato_nome)
            # Modify filename to include jersey number
            nome_slug = jogador["nome"].lower().replace(" ", "-")
            numero_camisa_slug = str(jogador["numero_camisa"]).replace("/", "-") # Handle potential slashes in N/A
            filename = f"{nome_slug}-{numero_camisa_slug}.{formato}" if jogador["numero_camisa"] != "N/A" else f"{nome_slug}.{formato}"
            salvar_dados(stats, os.path.join(pasta_time, "jogadores", filename), formato)
        except Exception as e:
            print(f"   ❌ Erro ao coletar jogador {jogador['nome']}: {e}")

def extrair_estatisticas_gerais_campeonato(driver):
    try:
        # Save page source to a file for inspection
        with open("page_source_campeonato.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'estatísticas')]"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        dados_gerais = {}

        # Find the main container for statistics
        # Looking for a div with specific classes that contains the 'estatísticas' span
        # Based on the new HTML, the container for general statistics is a div with class 'sc-hLBwJm gLqgJp' 
        estatisticas_container = soup.find("div", class_="sc-hLBwJm gLqgJp") 
        
        if estatisticas_container:
            # Find all rows within this container that hold key-value pairs
            # The rows are now 'div' elements with class 'sc-bczRLJ fqjJgC' 
            estatisticas_linhas = estatisticas_container.find_all("div", class_="sc-bczRLJ fqjJgC") 
            for linha in estatisticas_linhas:
                spans = linha.find_all("span")
                if len(spans) == 2:
                    chave = spans[0].text.strip()
                    valor = spans[1].text.strip()
                    dados_gerais[chave] = valor

        if not dados_gerais:
            print("❌ Não foi possível extrair as estatísticas gerais do campeonato. Verifique o layout da página ou os seletores.")

        print(f"✅ Estatísticas Gerais coletadas")
        return dados_gerais if dados_gerais else {}

    except Exception as e:
        print(f"❌ Erro ao coletar as estatísticas gerais: {e}")
        return {}


# =====================
# SofasCrawler
# =====================
if __name__ == "__main__":
    # Carregar o arquivo JSON com os campeonatos
    with open("campeonatos.json", "r", encoding="utf-8") as f:
        campeonatos = json.load(f)

    # Processa cada campeonato listado no JSON
    for campeonato in campeonatos:
        campeonato_nome = campeonato["campeonato_nome"]
        campeonato_ano = campeonato["campeonato_ano"]
        url_campeonato = campeonato["url_campeonato"]

        total_urls_visitadas = 0

        # Os arquivos podem ser salvos em txt ou json
        fortmato_arquivo = "txt"

        print(f"🏆 Coletando dados do campeonato {campeonato_nome} ({campeonato_ano})")

        driver = iniciar_driver()

        # Coletar estatísticas gerais do campeonato
        print("📊 Coletando estatísticas gerais do campeonato...")
        driver.get(url_campeonato)
        time.sleep(3)
        estatisticas_gerais = extrair_estatisticas_gerais_campeonato(driver)  
        salvar_dados(estatisticas_gerais, os.path.join("resultados", f"{campeonato_nome.lower().replace(' ', '-')}-{campeonato_ano}", "info_campeonato.txt"), formato=fortmato_arquivo)
        total_urls_visitadas += 1

        # Coletar dados dos times e jogadores
        print("📝 Coletando dados de times e jogadores...")
        urls_times = extrair_urls_times(driver, url_campeonato)  
        for url_time in urls_times:
            total_urls_visitadas += 1
            print(f"🔗 Visitando URL {total_urls_visitadas}/{len(urls_times)}: {url_time}")
            coletar_dados_time(driver, url_time, campeonato_nome, campeonato_ano, formato=fortmato_arquivo)  

        driver.quit()

    # Exibe o resumo final
    print("✅ Processamento concluído!")
    print(f"🔢 Total de URLs visitadas: {total_urls_visitadas}")
    print(f"📂 Total de arquivos criados: {total_arquivos_criados}")
