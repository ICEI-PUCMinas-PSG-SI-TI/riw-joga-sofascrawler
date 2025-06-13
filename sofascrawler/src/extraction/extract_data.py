import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import undetected_chromedriver as uc  # Biblioteca especial para evitar detecção

class SofaScoreCrawler:
    def __init__(self, base_dir='data'):
        self.base_dir = base_dir
        self.total_files = 0
        self.driver = self.init_driver()
        
    def init_driver(self):
        """Configura o driver do Chrome para evitar detecção"""
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        
        # Configurações para evitar detecção
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        driver = uc.Chrome(options=options)
        return driver
    
    def solve_captcha_manually(self):
        """Aguarda o usuário resolver o captcha manualmente"""
        print("\n⚠️ CAPTCHA DETECTADO! Por favor resolva manualmente:")
        print("1. Resolva o CAPTCHA na janela do navegador")
        print("2. Depois de resolver, volte aqui e pressione Enter para continuar...")
        input()
    
    def navigate_to_url(self, url):
        """Navega para a URL e verifica por CAPTCHA"""
        self.driver.get(url)
        time.sleep(5)  # Tempo para carregar a página
        
        # Verifica se apareceu um CAPTCHA
        if "captcha" in self.driver.page_source.lower():
            self.solve_captcha_manually()
    
    def extract_data(self):
        """Extrai dados após o CAPTCHA ser resolvido"""
        # Implemente sua lógica de extração aqui
        # Exemplo básico:
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        teams = []
        
        # Extrai times (ajuste os seletores conforme necessário)
        for team in soup.select('.team-row'):
            name = team.select_one('.team-name').text if team.select_one('.team-name') else 'Desconhecido'
            teams.append(name)
        
        return {'teams': teams}
    
    def save_data(self, data, filename):
        """Salva os dados extraídos"""
        os.makedirs(self.base_dir, exist_ok=True)
        with open(os.path.join(self.base_dir, filename), 'w') as f:
            json.dump(data, f)
        self.total_files += 1
    
    def run(self, url):
        """Executa o crawler completo"""
        try:
            self.navigate_to_url(url)
            data = self.extract_data()
            self.save_data(data, 'resultados.json')
            print(f"✅ Extração concluída! {self.total_files} arquivos salvos.")
        except Exception as e:
            print(f"❌ Erro durante a execução: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    print("""=== SofaScore Crawler ===
Este script irá:
1. Abrir o navegador automaticamente
2. Aguardar você resolver qualquer CAPTCHA manualmente
3. Extrair os dados após o CAPTCHA ser resolvido
""")
    
    # URL de exemplo - substitua pela que você deseja extrair
    TARGET_URL = "https://www.sofascore.com/torneio/futebol/italy/serie-a/23"
    
    crawler = SofaScoreCrawler()
    crawler.run(TARGET_URL)