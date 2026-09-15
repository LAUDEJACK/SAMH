import os
import joblib
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score


def treinar_rede_neural(caminho_dados: str, alvo: str = 'cota_mucum'):
    # 1. Carregar dados
    df = pd.read_csv(caminho_dados)

    colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', alvo]
    features = [col for col in df.columns if col not in colunas_ignorar and not col.startswith('Unnamed')]

    X = df[features]
    y = df[alvo]

    # 2. Divisão temporal (80% treino, 20% teste)
    limite = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:limite], X.iloc[limite:]
    y_train, y_test = y.iloc[:limite], y.iloc[limite:]

    # 3. Normalização dos Dados (Essencial para Redes Neurais)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Treinar a Rede Neural (Perceptron Multicamadas)
    print("\nTreinando a Rede Neural (MLP Regressor)...")
    mlp_model = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42
    )
    mlp_model.fit(X_train_scaled, y_train)

    # 5. Avaliação
    previsoes = mlp_model.predict(X_test_scaled)
    rmse = root_mean_squared_error(y_test, previsoes)
    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)

    print(f"\n--- Resultados da Rede Neural (MLP) ---")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"R²:   {r2:.4f}")

    # 6. Salvar modelo
    os.makedirs("models_saved", exist_ok=True)
    joblib.dump(mlp_model, "models_saved/mlp_model.pkl")
    joblib.dump(scaler, "models_saved/scaler_mlp.pkl")
    print("\nModelo salvo em: models_saved/mlp_model.pkl")


if __name__ == "__main__":
    CAMINHO_DATASET = "data/processed/dataset_treinamento.csv"
    if os.path.exists(CAMINHO_DATASET):
        treinar_rede_neural(CAMINHO_DATASET, alvo='cota_mucum')
    else:
        print(f"Arquivo não encontrado em: {CAMINHO_DATASET}")