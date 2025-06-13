import streamlit as st
import json
import pandas as pd

# -----------------------
# Carregamento de dados
def carregar_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

dados_jogadores = carregar_json("estatisticas_jogadores.json")
dados_times = carregar_json("estatisticas_times.json")
dados_campeonatos = carregar_json("estatisticas_campeonatos.json")

# -----------------------
# Página principal
st.set_page_config(page_title="Buscador de Estatísticas ⚽", layout="wide")
st.title("🔍 Buscador de Estatísticas de Campeonatos, Times e Jogadores")

tipo = st.radio("Selecione o que deseja buscar:", ["Jogadores", "Times", "Campeonatos"])

estatistica = st.text_input("Digite a estatística desejada (ex: gols, passes_certos, desarmes_por_jogo):")

top_n = st.number_input("Top N resultados", min_value=1, max_value=100, value=10)

ordem = st.radio("Ordenação:", ["Maior para menor", "Menor para maior"])
desc = True if ordem == "Maior para menor" else False

filtro_campeonato = ""
if tipo in ["Jogadores", "Times"]:
    todos_camps = sorted(set(list(dados_jogadores.keys()) + list(dados_times.keys())))
    filtro_campeonato = st.selectbox("Filtrar por campeonato (opcional):", [""] + todos_camps)

# -----------------------
# Função de busca
def buscar_jogadores():
    resultado = []
    for campeonato, times in dados_jogadores.items():
        if filtro_campeonato and campeonato != filtro_campeonato:
            continue
        for time, jogadores in times.items():
            for jogador, stats in jogadores.items():
                valor = stats.get(estatistica)
                if valor is not None:
                    resultado.append({
                        "Campeonato": campeonato,
                        "Time": time,
                        "Jogador": jogador,
                        estatistica: valor
                    })
    return pd.DataFrame(resultado)

def buscar_times():
    resultado = []
    for campeonato, times in dados_times.items():
        if filtro_campeonato and campeonato != filtro_campeonato:
            continue
        for time, stats in times.items():
            valor = stats.get(estatistica)
            if valor is not None:
                resultado.append({
                    "Campeonato": campeonato,
                    "Time": time,
                    estatistica: valor
                })
    return pd.DataFrame(resultado)

def buscar_campeonatos():
    resultado = []
    for campeonato, stats in dados_campeonatos.items():
        valor = stats.get(estatistica)
        if valor is not None:
            resultado.append({
                "Campeonato": campeonato,
                estatistica: valor
            })
    return pd.DataFrame(resultado)

# -----------------------
# Execução da busca
if estatistica:
    if tipo == "Jogadores":
        df = buscar_jogadores()
    elif tipo == "Times":
        df = buscar_times()
    else:
        df = buscar_campeonatos()

    if not df.empty:
        df_ordenado = df.sort_values(by=estatistica, ascending=not desc).head(top_n)
        st.success(f"✅ {len(df_ordenado)} resultados encontrados!")
        st.dataframe(df_ordenado, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum dado encontrado para essa estatística.")