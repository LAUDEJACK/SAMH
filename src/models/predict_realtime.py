import os
import joblib
import pandas as pd
import numpy as np


class PredictorEngine:
    """
    Engine responsável por carregar os artefatos treinados e
    realizar inferências em tempo real para a cota de Muçum.
    """

    def __init__(self, path_model: str = "models_saved/mlp_model.pkl",
                 path_scaler: str = "models_saved/scaler_mlp.pkl"):
        if not os.path.exists(path_model) or not os.path.exists(path_scaler):
            raise FileNotFoundError("Artefatos do modelo ou scaler não encontrados em models_saved/")

        self.model = joblib.load(path_model)
        self.scaler = joblib.load(path_scaler)

    def prever_cota(self, input_df: pd.DataFrame) -> float:
        """
        Recebe um DataFrame com as mesmas features do treinamento e retorna o valor previsto.
        """
        # Garante a ordenação correta das colunas esperadas pelo modelo
        X_scaled = self.scaler.transform(input_df)
        predicao = self.model.predict(X_scaled)
        return float(predicao[0])


if __name__ == "__main__":
    # Teste unitário de inferência utilizando a última linha do dataset ouro
    caminho_ouro = "data/processed/dataset_ouro_treinamento.csv"
    if os.path.exists(caminho_ouro):
        df_ouro = pd.read_csv(caminho_ouro)
        colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', 'cota_mucum']
        features = [col for col in df_ouro.columns if col not in colunas_ignorar and not col.startswith('Unnamed')]

        sample_input = df_ouro[features].iloc[[-1]]

        engine = PredictorEngine()
        cota_prevista = engine.prever_cota(sample_input)
        print(f"\n[TESTE DE INFERÊNCIA] Cota Prevista para Muçum: {cota_prevista:.2f} metros")