import os
import joblib
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score


def treinar_xgboost(caminho_dados: str, alvo: str = 'cota_mucum'):
    # 1. Carregar dados
    df = pd.read_csv(caminho_dados)

    # 2. Separar Features (X) e Target (y)
    colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', alvo]
    features = [col for col in df.columns if col not in colunas_ignorar and not col.startswith('Unnamed')]

    X = df[features]
    y = df[alvo]

    # 3. Divisão temporal (80% treino, 20% teste)
    limite = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:limite], X.iloc[limite:]
    y_train, y_test = y.iloc[:limite], y.iloc[limite:]

    # 4. Treinar modelo XGBoost
    print("\nTreinando o XGBoost Regressor...")
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, n_jobs=-1)
    xgb_model.fit(X_train, y_train)

    # 5. Avaliação
    previsoes = xgb_model.predict(X_test)
    rmse = root_mean_squared_error(y_test, previsoes)
    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)

    print(f"\n--- Resultados do XGBoost ---")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"R²:   {r2:.4f}")

    # 6. Salvar modelo
    os.makedirs("models_saved", exist_ok=True)
    caminho_salvar = "models_saved/xgboost.pkl"
    joblib.dump(xgb_model, caminho_salvar)
    print(f"\nModelo salvo com sucesso em: {caminho_salvar}")


if __name__ == "__main__":
    CAMINHO_DATASET = "data/processed/dataset_treinamento.csv"

    if os.path.exists(CAMINHO_DATASET):
        treinar_xgboost(CAMINHO_DATASET, alvo='cota_mucum')
    else:
        print(f"Arquivo não encontrado em: {CAMINHO_DATASET}")