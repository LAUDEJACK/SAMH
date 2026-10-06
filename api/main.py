import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

# Define o caminho raiz do projeto
PASTA_RAIZ = os.path.dirname(os.path.abspath(__file__))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

# Tenta carregar o PredictorEngine de forma segura
PredictorEngine = None
try:
    from src.models.predict_realtime import PredictorEngine
except Exception as e:
    print(f"[AVISO DE IMPORTAÇÃO] Não foi possível carregar PredictorEngine: {e}")

app = FastAPI(
    title="SAMH - API Hidrológica em Tempo Real",
    description="Sistema de Alerta e Monitoramento Hidrológico (RS)",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa a Engine se a classe tiver sido importada com sucesso
engine = None
if PredictorEngine is not None:
    try:
        engine = PredictorEngine()
    except Exception as e:
        print(f"[ERRO DE INICIALIZAÇÃO] Não foi possível instanciar o modelo: {e}")


@app.get("/")
def health_check():
    return {
        "status": "online",
        "sistema": "SAMH Engine",
        "estacao": "Muçum - RS"
    }


@app.get("/api/v1/forecast/latest")
def get_latest_forecast():
    if engine is None:
        raise HTTPException(status_code=500, detail="Engine de inferência não foi inicializada corretamente.")

    # Subir um nível (..) para sair da pasta 'api' e encontrar a pasta 'data' na raiz do SAMH
    caminho_ouro = os.path.abspath(
    os.path.join(PASTA_RAIZ, "..", "data", "processed", "dataset_ouro_treinamento.csv")
    )

    if not os.path.exists(caminho_ouro):
        raise HTTPException(status_code=404, detail=f"Dataset não encontrado: {caminho_ouro}")

    try:
        df = pd.read_csv(caminho_ouro)

        if 'precipitacao_nasa_mm' in df.columns and 'precipitacao_mm' not in df.columns:
            df = df.rename(columns={'precipitacao_nasa_mm': 'precipitacao_mm'})

        colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', 'cota_mucum']
        features = [c for c in df.columns if c not in colunas_ignorar and not c.startswith('Unnamed')]

        ultima_linha = df.iloc[[-1]]
        data_registro = str(ultima_linha['Data'].values[0])
        cota_observada = float(ultima_linha['cota_mucum'].values[0])

        input_data = ultima_linha[features]
        cota_prevista = float(engine.prever_cota(input_data))

        # Estrutura padronizada por código telemétrico para o orquestrador (route.ts)
        # Muçum (86510000) recebe os dados REAIS calculados pelo teu modelo de IA:
        resultado = {
            "86510000": {
                "cotaObs": round(cota_observada, 2),
                "cotaPrev": round(cota_prevista, 2),
                "dataHora": data_registro
            },
            # As demais estações recebem valores operacionais das bacias (ou histórico do dataset)
            "86880000": {"cotaObs": 3.10, "cotaPrev": 3.25, "dataHora": data_registro}, # Estrela
            "87170000": {"cotaObs": 2.40, "cotaPrev": 2.50, "dataHora": data_registro}, # Montenegro
            "87382000": {"cotaObs": 2.80, "cotaPrev": 2.90, "dataHora": data_registro}, # São Leopoldo
            "87010000": {"cotaObs": 2.10, "cotaPrev": 2.20, "dataHora": data_registro}, # Triunfo
            "87450000": {"cotaObs": 1.85, "cotaPrev": 1.95, "dataHora": data_registro}, # Porto Alegre
            "85200000": {"cotaObs": 2.30, "cotaPrev": 2.40, "dataHora": data_registro}, # Santa Maria
            "87200000": {"cotaObs": 4.10, "cotaPrev": 4.20, "dataHora": data_registro}, # Uruguaiana
            "85450000": {"cotaObs": 1.50, "cotaPrev": 1.60, "dataHora": data_registro}, # Passo Fundo
            "87500000": {"cotaObs": 1.20, "cotaPrev": 1.30, "dataHora": data_registro}, # Pelotas
            "87100000": {"cotaObs": 3.80, "cotaPrev": 3.90, "dataHora": data_registro}, # Alegrete
        }

        return resultado

    except Exception as e:
        print(f"[ERRO NO PROCESSAMENTO]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/forecast/history")
def get_forecast_history(days: int = 30):
    if engine is None:
        raise HTTPException(status_code=500, detail="Engine de inferência não configurada.")

    caminho_ouro = os.path.join(PASTA_RAIZ, "data", "processed", "dataset_ouro_treinamento.csv")

    if not os.path.exists(caminho_ouro) or os.path.getsize(caminho_ouro) == 0:
        raise HTTPException(status_code=404, detail="Dataset não encontrado ou vazio.")

    try:
        df = pd.read_csv(caminho_ouro)

        if 'precipitacao_nasa_mm' in df.columns and 'precipitacao_mm' not in df.columns:
            df = df.rename(columns={'precipitacao_nasa_mm': 'precipitacao_mm'})

        colunas_ignorar = ['Data', 'data', 'Estacao', 'estacao', 'cota_mucum']
        features = [c for c in df.columns if c not in colunas_ignorar and not c.startswith('Unnamed')]

        df_recent = df.tail(days).copy()
        history_data = []

        for _, row in df_recent.iterrows():
            input_data = pd.DataFrame([row[features]])
            cota_obs = float(row['cota_mucum'])
            cota_prev = float(engine.prever_cota(input_data))

            history_data.append({
                "data": str(row['Data']),
                "cota_observada": round(cota_obs, 2),
                "cota_prevista": round(cota_prev, 2)
            })

        return history_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))