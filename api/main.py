import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

# Garante a visibilidade dos módulos dentro de src/
PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

from src.models.predict_realtime import PredictorEngine

app = FastAPI(
    title="SIPH - API Hidrológica em Tempo Real",
    description="API de Previsão de Enchentes para Muçum (RS)",
    version="1.0.0"
)

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa a Engine de Predição
try:
    engine = PredictorEngine()
except Exception as e:
    print(f"[ERRO DE INICIALIZAÇÃO] Não foi possível carregar os modelos: {e}")
    engine = None


@app.get("/")
def health_check():
    return {
        "status": "online",
        "sistema": "SIPH Engine",
        "estacao": "Muçum - RS"
    }


@app.get("/api/v1/forecast/latest")
def get_latest_forecast():
    """
    Endpoint consumido pelo Frontend para obter a previsão atualizada.
    """
    if engine is None:
        raise HTTPException(status_code=500, detail="Engine de inferência não foi inicializada corretamente.")

    # Constrói o caminho absoluto para o arquivo CSV
    caminho_ouro = os.path.join(PASTA_RAIZ, "data", "processed", "dataset_ouro_treinamento.csv")

    if not os.path.exists(caminho_ouro):
        raise HTTPException(status_code=404, detail=f"Dataset não encontrado no caminho: {caminho_ouro}")

    try:
        df = pd.read_csv(caminho_ouro)

        # Padroniza coluna de precipitação se necessário
        if 'precipitacao_nasa_mm' in df.columns and 'precipitacao_mm' not in df.columns:
            df = df.rename(columns={'precipitacao_nasa_mm': 'precipitacao_mm'})

        # Filtra apenas colunas numéricas de entrada
        colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', 'cota_mucum']
        features = [c for c in df.columns if c not in colunas_ignorar and not c.startswith('Unnamed')]

        ultima_linha = df.iloc[[-1]]
        data_registro = str(ultima_linha['Data'].values[0])
        cota_observada = float(ultima_linha['cota_mucum'].values[0])

        input_data = ultima_linha[features]
        cota_prevista = float(engine.prever_cota(input_data))

        # Classificação do Risco Hidrológico
        status_alerta = "Normal"
        if cota_prevista >= 18.0:
            status_alerta = "Cota de Transbordamento / Emergência"
        elif cota_prevista >= 15.0:
            status_alerta = "Alerta de Enchente"
        elif cota_prevista >= 10.0:
            status_alerta = "Atenção"

        return {
            "data_referencia": data_registro,
            "estacao": "Muçum (RS)",
            "cota_observada_m": round(cota_observada, 2),
            "cota_prevista_m": round(cota_prevista, 2),
            "status_alerta": status_alerta
        }

    except Exception as e:
        print(f"[ERRO NO PROCESSAMENTO]: {e}")
        raise HTTPException(status_code=500, detail=str(e))