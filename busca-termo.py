import json

# Caminho do índice invertido gerado pela normalização
CAMINHO_INDICE = "resultados/indexacao_saida/indice_invertido.json"

# Carrega o índice invertido
with open(CAMINHO_INDICE, "r", encoding="utf-8") as f:
    indice_invertido = json.load(f)

# Loop de busca
print("🔎 Buscador por termo (digite 'sair' para encerrar)\n")

while True:
    termo = input("Digite um termo para buscar: ").strip().lower()
    
    if termo == "sair":
        break

    resultados = indice_invertido.get(termo)

    if resultados:
        print(f"\n📄 Termo '{termo}' encontrado em {len(resultados)} arquivo(s):")
        for ocorrencia in resultados:
            print(f" - {ocorrencia}")
    else:
        print(f"\n⚠️ Termo '{termo}' não encontrado em nenhum arquivo.\n")