import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests

PASTA_RAIZ = os.path.dirname(os.path.abspath(__file__))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

# Lista Oficial das 11 Estações do SAMH
ESTACOES = [
    {
        "codigo": "86510000",
        "nome": "Muçum",
        "rio": "Rio Taquari / Cabeceira",
        "bacia": "BACIA MUÇUM",
    },
    {
        "codigo": "86880000",
        "nome": "Estrela",
        "rio": "Rio Taquari / Vale",
        "bacia": "BACIA ESTRELA",
    },
    {
        "codigo": "87170000",
        "nome": "Montenegro",
        "rio": "Rio Caí",
        "bacia": "BACIA MONTENEGRO",
    },
    {
        "codigo": "87382000",
        "nome": "São Leopoldo",
        "rio": "Rio dos Sinos",
        "bacia": "BACIA SÃO LEOPOLDO",
    },
    {
        "codigo": "87010000",
        "nome": "Triunfo",
        "rio": "Rio Jacuí",
        "bacia": "BACIA TRIUNFO",
    },
    {
        "codigo": "87450000",
        "nome": "Porto Alegre",
        "rio": "Lago Guaíba / Desembocadura",
        "bacia": "BACIA PORTO ALEGRE",
    },
    {
        "codigo": "85200000",
        "nome": "Santa Maria / Central",
        "rio": "Rio Vacacaí",
        "bacia": "BACIA SANTA MARIA",
    },
    {
        "codigo": "87200000",
        "nome": "Uruguaiana / Fronteira Oeste",
        "rio": "Rio Uruguay",
        "bacia": "BACIA URUGUAIANA",
    },
    {
        "codigo": "85450000",
        "nome": "Passo Fundo / Norte",
        "rio": "Rio Passo Fundo / Uruguai",
        "bacia": "BACIA PASSO FUNDO",
    },
    {
        "codigo": "87500000",
        "nome": "Pelotas / Rio Grande",
        "rio": "Lagoa dos Patos / Rio Camaquã",
        "bacia": "BACIA PELOTAS",
    },
    {
        "codigo": "87100000",
        "nome": "Alegrete",
        "rio": "Rio Ibirapuitã / Ibicuí",
        "bacia": "BACIA ALEGRETE",
    },
]

DB_PATH = os.path.join(PASTA_RAIZ, "data", "samh_data.db")

PredictorEngine = None
try:
    from src.models.predict_realtime import PredictorEngine
except Exception as e:
    print(
        f"[AVISO DE IMPORTAÇÃO] Não foi possível carregar PredictorEngine: {e}"
    )

app = FastAPI(
    title="SAMH - API Hidrológica em Tempo Real",
    description="Sistema de Alerta e Monitoramento Hidrológico (RS)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = None
if PredictorEngine is not None:
    try:
        engine = PredictorEngine()
    except Exception as e:
        print(
            f"[ERRO DE INICIALIZAÇÃO] Não foi possível instanciar o modelo: {e}"
        )


# --- BANCO DE DADOS E INGESTÃO TELEMÉTRICA (A CADA 10 MINUTOS) ---


def inicializar_banco():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leituras_telemetricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_estacao TEXT NOT NULL,
            nome_estacao TEXT,
            rio TEXT,
            cota_observada REAL,
            data_hora TEXT NOT NULL,
            data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(codigo_estacao, data_hora)
        )
    """
    )
    conn.commit()
    conn.close()


def buscar_dados_ana(codigo_estacao):
    hoje = datetime.now()
    inicio = hoje - timedelta(days=3)

    dt_fim = hoje.strftime("%d/%m/%Y")
    dt_inicio = inicio.strftime("%d/%m/%Y")

    url = f"https://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometricos?codEstacao={codigo_estacao}&dataInicio={dt_inicio}&dataFim={dt_fim}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            leituras = []

            for item in root.findall(".//DadosHidrometereologicos"):
                nivel_elem = item.find("Nivel")
                data_elem = item.find("DataHora")

                if (
                    nivel_elem is not None
                    and nivel_elem.text
                    and data_elem is not None
                ):
                    try:
                        valor = float(nivel_elem.text)
                        if valor > 50:  # Converte centímetros para metros
                            valor = valor / 100.0

                        leituras.append(
                            {
                                "cota": round(valor, 2),
                                "data_hora": data_elem.text.strip(),
                            }
                        )
                    except ValueError:
                        continue
            return leituras
    except Exception as e:
        print(
            f"[SAMH INGESTÃO] Erro ao consultar estação {codigo_estacao} na ANA: {e}"
        )

    return []


def salvar_leituras(estacao, leituras):
    if not leituras:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    novos_registros = 0

    for l in leituras:
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO leituras_telemetricas 
                (codigo_estacao, nome_estacao, rio, cota_observada, data_hora)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    estacao["codigo"],
                    estacao["nome"],
                    estacao["rio"],
                    l["cota"],
                    l["data_hora"],
                ),
            )
            if cursor.rowcount > 0:
                novos_registros += 1
        except Exception:
            pass

    conn.commit()
    conn.close()


def loop_ingestao_background():
    inicializar_banco()
    while True:
        print(
            f"\n[SAMH INGESTÃO] Sincronizando estações telemétricas [{datetime.now().strftime('%H:%M:%S')}]..."
        )
        for est in ESTACOES:
            leituras = buscar_dados_ana(est["codigo"])
            salvar_leituras(est, leituras)
        print(
            "[SAMH INGESTÃO] Sincronização concluída. Próxima coleta em 10 minutos."
        )
        time.sleep(600)  # Intervalo de 10 minutos (600s)


@app.on_event("startup")
def startup_event():
    # Inicia a thread de ingestão contínua junto com o servidor FastAPI
    thread_ingestao = threading.Thread(
        target=loop_ingestao_background, daemon=True
    )
    thread_ingestao.start()


# --- ENDPOINTS DA API ---


@app.get("/")
def health_check():
    return {
        "status": "online",
        "sistema": "SAMH Engine",
        "estacoes_ativas": len(ESTACOES),
    }


@app.get("/api/v1/forecast/latest")
def get_latest_forecast():
    resultado = {}

    # 1. Busca as medições mais recentes registradas na base SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT codigo_estacao, cota_observada, data_hora
            FROM leituras_telemetricas
            WHERE id IN (
                SELECT MAX(id) FROM leituras_telemetricas GROUP BY codigo_estacao
            )
        """
        )
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            cod, cota, dt = row
            resultado[cod] = {
                "cotaObs": cota,
                "cotaPrev": round(cota * 1.01, 2),
                "dataHora": dt,
            }
    except Exception as e:
        print(f"[ERRO CONSULTA BANCO]: {e}")

    # 2. Injeta a predição da Engine de IA para a estação de Muçum (86510000)
    if engine is not None:
        caminho_ouro = os.path.join(
            PASTA_RAIZ, "data", "processed", "dataset_ouro_treinamento.csv"
        )
        if os.path.exists(caminho_ouro):
            try:
                df = pd.read_csv(caminho_ouro)
                if (
                    "precipitacao_nasa_mm" in df.columns
                    and "precipitacao_mm" not in df.columns
                ):
                    df = df.rename(
                        columns={"precipitacao_nasa_mm": "precipitacao_mm"}
                    )

                colunas_ignorar = [
                    "Data",
                    "data",
                    "Estacao",
                    "estacao",
                    "cota_mucum",
                ]
                features = [
                    c
                    for c in df.columns
                    if c not in colunas_ignorar and not c.startswith("Unnamed")
                ]

                ultima_linha = df.iloc[[-1]]
                cota_obs_mucum = float(ultima_linha["cota_mucum"].values[0])
                cota_prev_mucum = float(
                    engine.prever_cota(ultima_linha[features])
                )

                resultado["86510000"] = {
                    "cotaObs": round(cota_obs_mucum, 2),
                    "cotaPrev": round(cota_prev_mucum, 2),
                    "dataHora": str(ultima_linha["Data"].values[0]),
                }
            except Exception as e:
                print(f"[ERRO PREDIÇÃO MUÇUM]: {e}")

    return resultado


@app.get("/api/v1/forecast/history")
def get_forecast_history(days: int = 30):
    if engine is None:
        raise HTTPException(
            status_code=500, detail="Engine de inferência não configurada."
        )

    caminho_ouro = os.path.join(
        PASTA_RAIZ, "data", "processed", "dataset_ouro_treinamento.csv"
    )

    if not os.path.exists(caminho_ouro) or os.path.getsize(caminho_ouro) == 0:
        raise HTTPException(
            status_code=404, detail="Dataset não encontrado ou vazio."
        )

    try:
        df = pd.read_csv(caminho_ouro)

        if (
            "precipitacao_nasa_mm" in df.columns
            and "precipitacao_mm" not in df.columns
        ):
            df = df.rename(columns={"precipitacao_nasa_mm": "precipitacao_mm"})

        colunas_ignorar = ["Data", "data", "Estacao", "estacao", "cota_mucum"]
        features = [
            c
            for c in df.columns
            if c not in colunas_ignorar and not c.startswith("Unnamed")
        ]

        df_recent = df.tail(days).copy()
        history_data = []

        for _, row in df_recent.iterrows():
            input_data = pd.DataFrame([row[features]])
            cota_obs = float(row["cota_mucum"])
            cota_prev = float(engine.prever_cota(input_data))

            history_data.append(
                {
                    "data": str(row["Data"]),
                    "cota_observada": round(cota_obs, 2),
                    "cota_prevista": round(cota_prev, 2),
                }
            )

        return history_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))