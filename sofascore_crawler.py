import os
import time
import json
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configurações
BASE_DIR = "sofascore_data"
TIMEOUT = 3  # segundos para espera

def iniciar_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Configurações para evitar modais
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def criar_estrutura_diretorios():
    """Cria a estrutura de diretórios para armazenamento"""
    os.makedirs(BASE_DIR, exist_ok=True)

def nomear_arquivo(url):
    """Gera um nome de arquivo válido a partir da URL"""
    # Remove protocolo e domínio
    path = url.replace('https://www.sofascore.com', '')
    # Substitui caracteres inválidos
    path = path.replace('/', '_').replace('?', '_').replace('=', '_')
    return path[1:] + '.html' if path.startswith('_') else path + '.html'

def salvar_html(url, html):
    """Salva o HTML em um arquivo organizado por estrutura de URL"""
    caminho = os.path.join(BASE_DIR, nomear_arquivo(url))
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"💾 Página salva: {caminho}")

def coletar_pagina(driver, url):
    """Coleta o conteúdo HTML de uma página"""
    try:
        print(f"🌐 Acessando: {url}")
        driver.get(url)
        time.sleep(TIMEOUT)
        
        # Tentar fechar modais (cookies, newsletter, etc)
        try:
            driver.execute_script("""
                const botoes = [
                    ...document.querySelectorAll('button[aria-label*="Close"], button[aria-label*="Fechar"]'),
                    ...document.querySelectorAll('button:contains("Accept"), button:contains("Aceitar")')
                ];
                botoes.forEach(btn => btn.click());
            """)
            time.sleep(1)
        except:
            pass
        
        return driver.page_source
    except Exception as e:
        print(f"⚠️ Erro ao acessar {url}: {str(e)[:200]}")
        return None

def extrair_urls_jogadores(html_time):
    """Extrai URLs dos jogadores a partir da página do time"""
    soup = BeautifulSoup(html_time, 'html.parser')
    urls = set()
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/player/' in href and not href.startswith('http'):
            urls.add(f"https://www.sofascore.com{href}")
    
    return list(urls)

def processar_campeonato(driver, url_campeonato):
    """Processa um campeonato completo"""
    # Coletar página principal do campeonato
    html_campeonato = coletar_pagina(driver, url_campeonato)
    if html_campeonato:
        salvar_html(url_campeonato, html_campeonato)
    
    # Extrair URLs dos times
    driver.get(url_campeonato)
    time.sleep(TIMEOUT)
    html_campeonato = driver.page_source
    soup = BeautifulSoup(html_campeonato, 'html.parser')
    
    urls_times = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/team/futebol/' in href and not href.endswith('/futebol'):
            urls_times.add(f"https://www.sofascore.com{href}")
    
    print(f"🔍 Encontrados {len(urls_times)} times no campeonato")
    
    # Processar cada time
    for url_time in urls_times:
        # Coletar página do time
        html_time = coletar_pagina(driver, url_time)
        if not html_time:
            continue
            
        salvar_html(url_time, html_time)
        
        # Extrair e coletar páginas dos jogadores
        urls_jogadores = extrair_urls_jogadores(html_time)
        print(f"   👥 Encontrados {len(urls_jogadores)} jogadores no time")
        
        for url_jogador in urls_jogadores:
            html_jogador = coletar_pagina(driver, url_jogador)
            if html_jogador:
                salvar_html(url_jogador, html_jogador)

def main():
    criar_estrutura_diretorios()
    
    # Carregar configuração de campeonatos
    with open('campeonatos.json', 'r', encoding='utf-8') as f:
        campeonatos = json.load(f)
    
    driver = iniciar_driver()
    try:
        for campeonato in campeonatos:
            print(f"\n🏆 Processando {campeonato['campeonato_nome']} {campeonato['campeonato_ano']}")
            processar_campeonato(driver, campeonato['url_campeonato'])
    finally:
        driver.quit()
        print("\n✅ Todas as páginas foram coletadas com sucesso!")

if __name__ == "__main__":
    main()