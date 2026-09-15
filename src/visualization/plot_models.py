import os
import pandas as pd
import matplotlib.pyplot as plt
import joblib


def plotar_comparativo_modelos(caminho_dados: str, alvo: str = 'cota_mucum'):
    df = pd.read_csv(caminho_dados)

    colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', alvo]
    features = [col for col in df.columns if col not in colunas_ignorar and not col.startswith('Unnamed')]

    X = df[features]
    y = df[alvo]

    # Split temporal (mesmo do treinamento)
    limite = int(len(df) * 0.8)
    X_test = X.iloc[limite:]
    y_test = y.iloc[limite:].values

    plt.figure(figsize=(14, 6))
    plt.plot(y_test, label='Valor Real (Observado)', color='black', linewidth=1.5, linestyle='--')

    # 1. Random Forest
    if os.path.exists("models_saved/random_forest.pkl"):
        rf = joblib.load("models_saved/random_forest.pkl")
        plt.plot(rf.predict(X_test), label='Random Forest (R²: 0.7028)', alpha=0.7)

    # 2. XGBoost
    if os.path.exists("models_saved/xgboost.pkl"):
        xgb = joblib.load("models_saved/xgboost.pkl")
        plt.plot(xgb.predict(X_test), label='XGBoost (R²: 0.7293)', alpha=0.8)

    # 3. Rede Neural (MLP)
    if os.path.exists("models_saved/mlp_model.pkl") and os.path.exists("models_saved/scaler_mlp.pkl"):
        mlp = joblib.load("models_saved/mlp_model.pkl")
        scaler = joblib.load("models_saved/scaler_mlp.pkl")
        X_test_scaled = scaler.transform(X_test)
        plt.plot(mlp.predict(X_test_scaled), label='Rede Neural MLP (R²: 0.7556)', color='red', linewidth=1.2)

    plt.title(f'Comparativo de Desempenho dos Modelos - Estação {alvo.upper()}', fontsize=14, pad=15)
    plt.xlabel('Período de Teste (Dias)', fontsize=12)
    plt.ylabel('Cota (m)', fontsize=12)
    plt.legend(loc='upper right', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Salvar em reports
    pasta_reports = os.path.join("src", "visualization", "reports")
    os.makedirs(pasta_reports, exist_ok=True)
    caminho_salvar = os.path.join(pasta_reports, "comparacao_previsoes.png")

    plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
    print(f"\n[SUCESSO] Gráfico comparativo salvo em: {caminho_salvar}")
    plt.show()


if __name__ == "__main__":
    CAMINHO_DATASET = "data/processed/dataset_treinamento.csv"
    if os.path.exists(CAMINHO_DATASET):
        plotar_comparativo_modelos(CAMINHO_DATASET, alvo='cota_mucum')
    else:
        print(f"Dataset não encontrado em: {CAMINHO_DATASET}")