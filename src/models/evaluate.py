import os
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score


def avaliar_modelos(caminho_dados: str, alvo: str = 'cota_mucum'):
    df = pd.read_csv(caminho_dados)

    colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', alvo]
    features = [col for col in df.columns if col not in colunas_ignorar and not col.startswith('Unnamed')]

    X = df[features]
    y = df[alvo]

    # Divisão temporal (mesmo split usado nos treinos)
    limite = int(len(df) * 0.8)
    X_test = X.iloc[limite:]
    y_test = y.iloc[limite:]

    resultados = []

    # 1. Avaliar Random Forest
    if os.path.exists("models_saved/random_forest.pkl"):
        rf = joblib.load("models_saved/random_forest.pkl")
        pred = rf.predict(X_test)
        resultados.append({
            'Modelo': 'Random Forest',
            'RMSE': root_mean_squared_error(y_test, pred),
            'MAE': mean_absolute_error(y_test, pred),
            'R2': r2_score(y_test, pred)
        })

    # 2. Avaliar XGBoost
    if os.path.exists("models_saved/xgboost.pkl"):
        xgb = joblib.load("models_saved/xgboost.pkl")
        pred = xgb.predict(X_test)
        resultados.append({
            'Modelo': 'XGBoost',
            'RMSE': root_mean_squared_error(y_test, pred),
            'MAE': mean_absolute_error(y_test, pred),
            'R2': r2_score(y_test, pred)
        })

    # 3. Avaliar Rede Neural (MLP)
    if os.path.exists("models_saved/mlp_model.pkl") and os.path.exists("models_saved/scaler_mlp.pkl"):
        mlp = joblib.load("models_saved/mlp_model.pkl")
        scaler = joblib.load("models_saved/scaler_mlp.pkl")
        X_test_scaled = scaler.transform(X_test)
        pred = mlp.predict(X_test_scaled)
        resultados.append({
            'Modelo': 'Rede Neural (MLP)',
            'RMSE': root_mean_squared_error(y_test, pred),
            'MAE': mean_absolute_error(y_test, pred),
            'R2': r2_score(y_test, pred)
        })

    # Criar DataFrame resumo
    df_resumo = pd.DataFrame(resultados).sort_values(by='R2', ascending=False)

    print("\n================ TABELA COMPARATIVA DE MODELOS ================")
    print(df_resumo.to_string(index=False))

    # Salvar relatório final
    os.makedirs("reports", exist_ok=True)
    caminho_relatorio = "reports/desempenho_modelos.csv"
    df_resumo.to_csv(caminho_relatorio, index=False)
    print(f"\nRelatório salvo com sucesso em: {caminho_relatorio}")


if __name__ == "__main__":
    CAMINHO_DATASET = "data/processed/dataset_treinamento.csv"
    if os.path.exists(CAMINHO_DATASET):
        avaliar_modelos(CAMINHO_DATASET, alvo='cota_mucum')
    else:
        print(f"Arquivo não encontrado em: {CAMINHO_DATASET}")