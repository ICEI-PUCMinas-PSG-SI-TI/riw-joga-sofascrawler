import os
import json
from bs4 import BeautifulSoup
from collections import defaultdict

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
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    dados = defaultdict(dict)

    # --- Extração do Nome do Jogador (Provavelmente já está robusto) ---
    nome = None
    meta_nome = soup.find("meta", itemprop="name")
    if meta_nome and meta_nome.get("content"):
        nome = meta_nome["content"].strip()

    if not nome:
        titulo = soup.title
        if titulo:
            # Ajuste a string de remoção se o título tiver um formato diferente
            nome = titulo.text.replace("Estatísticas, avaliações e gols de", "").strip()
            # Exemplo: Se o título for "Nome do Jogador - Sofascore", você pode usar:
            # nome = titulo.text.split(' - ')[0].strip()

    dados["Jogador"] = nome or "Desconhecido"

    # --- Extração de Time e Contrato (Área que precisa de inspeção) ---
    # A abordagem atual de procurar por "Contrato até" em qualquer span é frágil.
    # É melhor encontrar um container específico para as informações do jogador
    # e depois procurar o time e o contrato dentro dele.

    time = "Desconhecido"
    contrato = "Desconhecido"

    # PASSO 1: Inspecione seu HTML. Encontre o elemento (geralmente uma div)
    # que contém o nome do time e a data do contrato.
    # Procure por uma classe estável (ex: "player-info-card", "team-contract-details")
    # ou um ID (ex: "playerDetails").

    # Exemplo hipotético:
    # player_info_container = soup.find("div", class_="player-info-container")
    # OU: player_info_container = soup.find("div", id="playerDetails")

    # Se você encontrar um container estável:
    # if player_info_container:
    #     # PASSO 2: Dentro desse container, encontre o span/div do time e do contrato.
    #     # Eles podem ter classes específicas ou você pode precisar navegar pela estrutura.
    #     # Exemplo:
    #     team_element = player_info_container.find("span", class_="team-name")
    #     contract_element = player_info_container.find("span", class_="contract-date")

    #     if team_element:
    #         time = team_element.text.strip()
    #     if contract_element:
    #         contrato = contract_element.text.strip()

    # Se não houver um container específico, mas os spans tiverem classes estáveis:
    # Exemplo:
    team_span = soup.find("span", class_="player-team-name") # Substitua por uma classe estável real
    contract_span = soup.find("span", class_="player-contract-info") # Substitua por uma classe estável real

    if team_span:
        time = team_span.text.strip()
    if contract_span:
        contrato = contract_span.text.strip()
    else:
        # Fallback para a sua lógica original se não encontrar classes estáveis para time/contrato
        # Mas esta parte ainda é frágil e deve ser evitada se possível.
        for span in soup.find_all("span"):
            texto = span.get_text(strip=True)
            if "Contrato até" in texto:
                # Tenta extrair o time da parte anterior, se a estrutura permitir
                partes = texto.split("Contrato até")
                if len(partes) == 2 and partes[0].strip(): # Verifica se há algo antes de "Contrato até"
                    time = partes[0].strip()
                    contrato = "Contrato até " + partes[1].strip()
                else:
                    contrato = texto
                break # Sai do loop assim que encontrar o primeiro contrato

    dados["Time"] = time
    dados["Contrato"] = contrato

    # --- Seções de Estatísticas (Área Crítica que Precisa de Inspeção Profunda) ---
    # A classe "Box Flex dlyXLO bnpRyo" é dinâmica e não funcionará.
    # Você precisa encontrar um seletor mais estável para as divs que contêm as estatísticas.

    # PASSO 1: Inspecione seu HTML. Encontre o container geral das estatísticas.
    # Exemplo: <div class="player-stats-sections"> ou <section id="playerStats">
    stats_main_container = soup.find("div", class_="player-stats-container") # Substitua por uma classe/ID estável

    if stats_main_container:
        # PASSO 2: Dentro do container principal, encontre as divs que representam cada seção (Partidas, Ataque, Passe, etc.).
        # Elas podem ter uma classe comum, como "stats-category" ou "section-block".
        # Exemplo:
        for section_div in stats_main_container.find_all("div", class_="stats-category-block"): # Substitua por uma classe estável
            # PASSO 3: Dentro de cada seção, encontre o título da seção (ex: "Passe").
            # Pode ser um <h3>, <h2>, ou um <span> com uma classe específica.
            section_title_element = section_div.find("h3", class_="category-title") # Substitua por uma tag/classe estável
            if section_title_element:
                secao_atual = section_title_element.text.strip()
                dados[secao_atual] = {}

                # PASSO 4: Dentro de cada seção, encontre os pares chave-valor das estatísticas.
                # Eles geralmente estão em divs ou li's com classes comuns.
                # Exemplo:
                for stat_item in section_div.find_all("div", class_="stat-row"): # Substitua por uma classe estável
                    key_element = stat_item.find("span", class_="stat-label") # Substitua por uma classe estável
                    value_element = stat_item.find("span", class_="stat-value") # Substitua por uma classe estável

                    if key_element and value_element:
                        chave = key_element.text.strip()
                        valor = value_element.text.strip()
                        dados[secao_atual][chave] = valor
    else:
        print("Aviso: Não foi possível encontrar o container principal de estatísticas. Verifique os seletores.")


    # --- Nota Sofascore (Área Crítica que Precisa de Inspeção) ---
    # A classe "sc-himrzO iaYywV" é dinâmica e não funcionará.
    # Procure por uma classe mais estável ou um atributo data-* ou itemprop.

    # Exemplo hipotético:
    # nota_element = soup.find("span", class_="player-rating-value")
    # OU: nota_element = soup.find("span", itemprop="ratingValue")
    # OU: nota_element = soup.find("span", attrs={"data-testid": "player-rating"})

    nota_element = soup.find("span", class_="player-rating-score") # Substitua por uma classe/ID/atributo estável
    if nota_element:
        dados["Nota Sofascore"] = {"Média": nota_element.text.strip()}
    else:
        print("Aviso: Não foi possível encontrar a nota Sofascore. Verifique os seletores.")

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
