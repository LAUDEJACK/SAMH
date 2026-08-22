import pandas as pd
import matplotlib

# Define o backend interativo para abrir a janela pop-up no Windows
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import os

# Descobre a verdadeira raiz do projeto SIPH
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = diretorio_atual

while not os.path.exists(os.path.join(raiz_projeto, "main.py")):
    pai = os.path.dirname(raiz_projeto)
    if pai == raiz_projeto:
        break
    raiz_projeto = pai

PASTA_PROCESSED = os.path.join(raiz_projeto, "data", "processed")
PASTA_IMAGENS = os.path.join(raiz_projeto, "reports", "figures")

ESTACOES = {
    "86510000": "Muçum (Rio Taquari)",
    "87170000": "Montenegro (Rio Caí)",
    "87382000": "São Leopoldo (Rio dos Sinos)"
}


def plotar_historico():
    os.makedirs(PASTA_IMAGENS, exist_ok=True)

    plt.figure(figsize=(15, 7))
    encontrou_algum = False

    for cod_estacao, nome_estacao in ESTACOES.items():
        caminho_csv = os.path.join(PASTA_PROCESSED, f"{cod_estacao}_cotas_diarias.csv")

        if os.path.exists(caminho_csv):
            encontrou_algum = True
            df = pd.read_csv(caminho_csv)
            df['Data'] = pd.to_datetime(df['Data'])

            df_filtrado = df[(df['Data'] >= '1973-01-01') & (df['Data'] <= '2023-12-31')]
            plt.plot(df_filtrado['Data'], df_filtrado['Cota_cm'] / 100, label=nome_estacao, alpha=0.7, linewidth=0.8)
            print(f"[INFO] Lançando no gráfico: {nome_estacao}")
        else:
            print(f"[AVISO] Arquivo não encontrado: {caminho_csv}")

    if not encontrou_algum:
        print("[ERRO] Nenhuma estação processada foi localizada.")
        return

    plt.title("Série Temporal de Cotas Diárias (1973 - 2023)", fontsize=14, fontweight='bold')
    plt.xlabel("Ano", fontsize=12)
    plt.ylabel("Cota (metros)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")

    # 1. Salva a imagem no disco
    caminho_grafico = os.path.join(PASTA_IMAGENS, "historico_cotas_1973_2023.png")
    plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
    print(f"\n[SUCESSO] Gráfico gerado e salvo em:\n{caminho_grafico}")

    # 2. Exibe a Janela Pop-up na tela
    print("[INFO] Abrindo janela de visualização...")
    plt.show()


if __name__ == "__main__":
    plotar_historico()