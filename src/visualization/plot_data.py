import os
import matplotlib.pyplot as plt
import pandas as pd


def plotar_serie_cotas(caminho_csv: str):
    # Carrega os dados processados
    df = pd.read_csv(caminho_csv)
    df["data"] = pd.to_datetime(df["data"])

    # Configura o gráfico
    plt.figure(figsize=(12, 5))
    plt.plot(
        df["data"],
        df["cota_cm"],
        color="royalblue",
        linewidth=1,
        label="Cota (cm)",
    )

    plt.title("Série Temporal de Cotas Diárias - Estação 86850000")
    plt.xlabel("Data")
    plt.ylabel("Cota (cm)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # Salva o gráfico gerado
    pasta_reports = os.path.join("reports", "figures")
    os.makedirs(pasta_reports, exist_ok=True)
    caminho_figura = os.path.join(pasta_reports, "grafico_cotas_86850000.png")

    plt.savefig(caminho_figura, dpi=300)
    print(f"Gráfico salvo com sucesso em: {caminho_figura}")
    plt.show()


if __name__ == "__main__":
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.abspath(os.path.join(diretorio_atual, "..", ".."))

    arquivo_processado = os.path.join(
        raiz_projeto, "data", "processed", "86850000_cotas_diarias.csv"
    )

    if os.path.exists(arquivo_processado):
        plotar_serie_cotas(arquivo_processado)
    else:
        print(f"Arquivo não encontrado: {arquivo_processado}")