import os
import sqlite3
import time
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import requests

# 11 Estações Telemétricas do RS
ESTACOES = [
    {'codigo': '86510000', 'nome': 'Muçum', 'rio': 'Rio Taquari / Cabeceira'},
    {'codigo': '86880000', 'nome': 'Estrela', 'rio': 'Rio Taquari / Médio'},
    {'codigo': '87170000', 'nome': 'Montenegro', 'rio': 'Rio Caí'},
    {'codigo': '87382000', 'nome': 'São Leopoldo', 'rio': 'Rio dos Sinos'},
    {'codigo': '87010000', 'nome': 'Triunfo', 'rio': 'Rio Jacuí'},
    {'codigo': '87450000', 'nome': 'Porto Alegre', 'rio': 'Guaíba'},
    {'codigo': '85200000', 'nome': 'Santa Maria', 'rio': 'Rio Vacacaí-Mirim'},
    {'codigo': '87200000', 'nome': 'Uruguaiana', 'rio': 'Rio Uruguai'},
    {'codigo': '85450000', 'nome': 'Passo Fundo', 'rio': 'Rio Passo Fundo'},
    {'codigo': '87500000', 'nome': 'Pelotas', 'rio': 'Canal São Gonçalo'},
    {'codigo': '87100000', 'nome': 'Alegrete', 'rio': 'Rio Ibirapuitã'},
]

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "samh_data.db")


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
                        if valor > 50:  # Ajuste cm para metros
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
            f"[ERRO] Falha ao consultar estação {codigo_estacao} na API da ANA: {e}"
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
        except Exception as err:
            pass

    conn.commit()
    conn.close()
    if novos_registros > 0:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] {estacao['nome']}: {novos_registros} novos dados inseridos."
        )


def executar_pipeline_ingestao():
    print(
        f"\n--- Iniciando ciclo de ingestão SAMH [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ---"
    )
    inicializar_banco()

    for est in ESTACOES:
        leituras = buscar_dados_ana(est["codigo"])
        salvar_leituras(est, leituras)

    print("--- Ciclo concluído. A aguardar 10 minutos para a próxima busca. ---")


if __name__ == "__main__":
    inicializar_banco()
    while True:
        executar_pipeline_ingestao()
        time.sleep(600)  # 600 segundos = 10 minutos