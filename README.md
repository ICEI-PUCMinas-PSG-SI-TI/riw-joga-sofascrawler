# SofasCrawler

O **SofasCrawler** é um script em Python desenvolvido para coletar estatísticas detalhadas de campeonatos, times e jogadores de futebol diretamente do site **SofaScore**. Ele utiliza **Selenium** e **BeautifulSoup** para navegar pelas páginas, extrair informações e salvar os dados obtidos em arquivos de texto ou JSON.

---

## 📋 Funcionalidades

1. **Coleta de Estatísticas Gerais do Campeonato**:
   - Estatísticas agregadas do campeonato, como gols marcados, passes realizados, etc.

2. **Coleta de Dados dos Times**:
   - Estatísticas gerais de cada time em categorias como ataque, defesa, precisão de passe, entre outras.

3. **Coleta de Dados dos Jogadores**:
   - Características individuais dos jogadores, como posição, idade, e estatísticas detalhadas (partidas jogadas, gols, passes, etc.).

4. **Armazenamento Estruturado**:
   - Os dados coletados são salvos em arquivos de texto ou JSON organizados em pastas específicas.

---

## 🛑 Limitações

Atualmente, o script **SofasCrawler** só funciona para páginas de campeonatos que adotam o formato **pontos corridos**. Caso o campeonato utilize outros formatos (como eliminatórias ou fases de grupos), a extração de dados pode não funcionar corretamente devido a diferenças no layout das páginas.

---

## 🛠️ Dependências

As seguintes bibliotecas são necessárias para executar o script:

- **Selenium**: Para automatizar a interação com o navegador.
- **BeautifulSoup4**: Para analisar e extrair dados do HTML.
- **Chromedriver**: Driver necessário para controlar o navegador Google Chrome via Selenium.
- **os** e **json** (nativo do Python): Para manipulação de arquivos e leitura de configurações.

---

## 📦 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/ICEI-PUCMinas-PSG-SI-TI/riw-joga-sofascrawler.git
cd SofasCrawler
```

### 2. Crie um Ambiente Virtual
Recomenda-se criar um ambiente virtual para gerenciar as dependências do projeto.
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

### 3. Instale as Dependências
Instale as bibliotecas necessárias listadas no arquivo `requirements.txt`.
```bash
pip install -r requirements.txt
```

### 4. Configure o Chromedriver
Baixe o **Chromedriver** compatível com a versão do Google Chrome instalada na sua máquina. 
- [Download do Chromedriver](https://chromedriver.chromium.org/downloads)
- Após o download, certifique-se de que o executável está no **PATH** do sistema ou no diretório do projeto.

### 5. Configuração no WSL (Windows Subsystem for Linux)

Se você estiver executando o script no WSL, será necessário instalar o Google Chrome e o Chromedriver. Siga os passos abaixo:

#### Passo 1: Instale o Google Chrome no WSL
Execute os seguintes comandos para instalar o Chrome no seu ambiente WSL:
```bash
sudo apt update
sudo apt install -y wget gnupg
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install -y google-chrome-stable
```

#### Passo 2: Instale o Chromedriver
Baixe e instale o Chromedriver compatível com a versão do Google Chrome instalada:
```bash
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
wget https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
rm chromedriver_linux64.zip
```

#### Passo 3: Verifique se o Chrome e o Chromedriver estão funcionando
Certifique-se de que o Chrome e o Chromedriver estão instalados corretamente:
```bash
google-chrome --version
chromedriver --version
```

#### Passo 4: Permita Renderização Gráfica no WSL (Opcional, se não for headless)
Caso você precise executar o Chrome em modo não headless (com interface gráfica), será necessário configurar um servidor X11, como o **VcXsrv** ou **Xming**, no Windows e exportar a variável de ambiente `DISPLAY`:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

Porém, como o script utiliza o modo headless por padrão, essa configuração geralmente é opcional.

### 6. Configuração do Arquivo `campeonatos.json`
Crie um arquivo `campeonatos.json` seguindo o formato abaixo:

```json
[
    {
        "campeonato_nome": "Campeonato Brasileiro",
        "campeonato_ano": "2025",
        "url_campeonato": "https://www.sofascore.com/pt/torneio/futebol/brasileiro-serie-a/325"
    },
    {
        "campeonato_nome": "Liga dos Campeões",
        "campeonato_ano": "24/25",
        "url_campeonato": "https://www.sofascore.com/pt/torneio/futebol/uefa-champions-league/7"
    }
]
```

---

## 🚀 Execução

Para executar o script, utilize o comando:
```bash
python sofascrawler.py
```

---

## 📂 Estrutura de Saída

Os dados coletados serão armazenados na pasta `resultados` com a seguinte estrutura hierárquica:

```
resultados/
└── nome-do-campeonato-ano/
    ├── info_campeonato.txt
    ├── nome-do-time/
    │   ├── info_time.txt
    │   └── jogadores/
    │       ├── nome-do-jogador.txt
    │       ├── ...
```

---

## 🧪 Testes e Debug

### Comando para Testar o Selenium
Certifique-se de que o Selenium está configurado corretamente:
```python
from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://www.google.com")
print(driver.title)
driver.quit()
```

---

## ⚠️ Observações

1. **Alterações no Layout do Site**: O script depende da estrutura atual do site SofaScore. Alterações no layout podem quebrar os seletores utilizados.
2. **Performance**: Dependendo do número de times e jogadores, o tempo de execução pode ser elevado.
3. **Captcha**: Em alguns casos, o site pode apresentar captchas para evitar automações. Certifique-se de não executar o script em excesso para evitar bloqueios.

---

## 📘 Referências

- [Documentação Selenium](https://selenium.dev/documentation/)
- [Documentação BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [SofaScore](https://www.sofascore.com/)
