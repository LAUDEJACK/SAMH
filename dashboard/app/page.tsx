'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const MapaRS = dynamic(() => import('./components/MapaRS'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[220px] bg-[#072017] flex items-center justify-center text-emerald-400/50 text-xs rounded-lg border border-[#0e3829]">
      Carregando Geoprocessamento do RS...
    </div>
  )
});

interface EstacaoData {
  codigo: string;
  nome: string;
  rio: string;
  cotaObs: number | null;
  cotaPrev: number | null;
  cotaAlerta: number;
  cotaInundacao: number;
  lat: number;
  lon: number;
}

interface HistoryData {
  data: string;
  cota_observada: number;
  cota_prevista: number;
}

interface HourlyData {
  hora: string;
  cota_observada: number;
  cota_prevista: number;
}

interface WeatherData {
  tempCurrent: number;
  humidity: number;
  wind: number;
  rainProb: number;
  condition: string;
  cidade: string;
}

const ESTACOES_11_BACIAS: EstacaoData[] = [
  { codigo: '86510000', nome: 'Muçum', rio: 'Rio Taquari / Cabeceira', cotaObs: 18.50, cotaPrev: 19.20, cotaAlerta: 18.00, cotaInundacao: 22.00, lat: -29.0833, lon: -51.8667 },
  { codigo: '86880000', nome: 'Estrela', rio: 'Rio Taquari', cotaObs: 19.80, cotaPrev: 20.40, cotaAlerta: 17.00, cotaInundacao: 19.00, lat: -29.5000, lon: -51.9667 },
  { codigo: '87170000', nome: 'Montenegro', rio: 'Rio Caí', cotaObs: 6.30, cotaPrev: 6.60, cotaAlerta: 5.00, cotaInundacao: 6.00, lat: -29.6833, lon: -51.4667 },
  { codigo: '87382000', nome: 'São Leopoldo', rio: 'Rio dos Sinos', cotaObs: 4.80, cotaPrev: 5.00, cotaAlerta: 4.50, cotaInundacao: 5.10, lat: -29.7600, lon: -51.1467 },
  { codigo: '87010000', nome: 'Triunfo', rio: 'Rio Jacuí', cotaObs: 4.70, cotaPrev: 4.90, cotaAlerta: 4.50, cotaInundacao: 5.50, lat: -29.9333, lon: -51.7167 },
  { codigo: '87450000', nome: 'Porto Alegre', rio: 'Guaíba', cotaObs: 3.15, cotaPrev: 3.30, cotaAlerta: 3.00, cotaInundacao: 3.60, lat: -30.0346, lon: -51.2177 },
  { codigo: '85200000', nome: 'Santa Maria', rio: 'Rio Vacacaí-Mirim', cotaObs: 5.80, cotaPrev: 6.10, cotaAlerta: 5.50, cotaInundacao: 6.50, lat: -29.6842, lon: -53.8069 },
  { codigo: '87200000', nome: 'Uruguaiana', rio: 'Rio Uruguay', cotaObs: 8.90, cotaPrev: 9.10, cotaAlerta: 8.50, cotaInundacao: 10.00, lat: -29.7547, lon: -57.0883 },
  { codigo: '85450000', nome: 'Passo Fundo', rio: 'Rio Passo Fundo', cotaObs: 2.10, cotaPrev: 2.15, cotaAlerta: 4.00, cotaInundacao: 5.00, lat: -28.2612, lon: -52.4083 },
  { codigo: '87500000', nome: 'Pelotas', rio: 'Canal de São Gonçalo', cotaObs: 1.70, cotaPrev: 1.75, cotaAlerta: 2.50, cotaInundacao: 3.00, lat: -31.7654, lon: -52.3376 },
  { codigo: '87100000', nome: 'Alegrete', rio: 'Rio Ibirapuitã', cotaObs: 9.80, cotaPrev: 10.10, cotaAlerta: 8.50, cotaInundacao: 9.70, lat: -29.7839, lon: -55.7919 },
];

const CIDADE_COORDS: Record<string, { lat: number; lon: number; nome: string }> = {
  '86510000': { lat: -29.0833, lon: -51.8667, nome: 'Muçum' },
  '86880000': { lat: -29.5000, lon: -51.9667, nome: 'Estrela' },
  '87170000': { lat: -29.6833, lon: -51.4667, nome: 'Montenegro' },
  '87382000': { lat: -29.7600, lon: -51.1467, nome: 'São Leopoldo' },
  '87010000': { lat: -29.9333, lon: -51.7167, nome: 'Triunfo' },
  '87450000': { lat: -30.0346, lon: -51.2177, nome: 'Porto Alegre' },
  '85200000': { lat: -29.6842, lon: -53.8069, nome: 'Santa Maria' },
  '87200000': { lat: -29.7547, lon: -57.0883, nome: 'Uruguaiana' },
  '85450000': { lat: -28.2612, lon: -52.4083, nome: 'Passo Fundo' },
  '87500000': { lat: -31.7654, lon: -52.3376, nome: 'Pelotas' },
  '87100000': { lat: -29.7839, lon: -55.7919, nome: 'Alegrete' },
};

function calcularStatus(est: EstacaoData): { texto: string; cor: string } {
  const cota = est.cotaObs;
  if (cota === null || cota === undefined) return { texto: 'SEM SINAL TELEMÉTRICO', cor: 'text-gray-400' };
  if (cota >= est.cotaInundacao) return { texto: 'NÍVEL CRÍTICO (INUNDAÇÃO)', cor: 'text-red-500' };
  if (cota >= est.cotaAlerta) return { texto: 'NÍVEL ELEVADO (ALERTA)', cor: 'text-orange-400' };
  if (cota < 1.0) return { texto: 'NÍVEL BAIXO', cor: 'text-amber-400' };
  return { texto: 'NÍVEL NORMAL', cor: 'text-emerald-400' };
}

function gerarDadosHoje(codigoEstacao: string, cotaAtual: number | null): HourlyData[] {
  const cotaValida = cotaAtual ?? 0;
  const horas = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'];
  const perfis: Record<string, number[]> = {
    '86510000': [-0.02, -0.01, 0.00, 0.01, 0.01, 0.00, -0.01, -0.01],
    '86880000': [0.03, 0.02, 0.01, 0.00, -0.01, -0.02, -0.03, -0.03],
    '87170000': [-0.02, -0.01, 0.00, 0.01, 0.02, 0.03, 0.02, 0.01],
    '87382000': [-0.01, 0.00, 0.01, 0.00, -0.01, 0.00, 0.01, 0.00],
    '87010000': [-0.02, -0.01, 0.01, 0.03, 0.02, 0.00, -0.01, -0.02],
    '87450000': [0.01, 0.00, -0.01, 0.00, 0.01, 0.00, -0.01, 0.00],
  };

  const variacoes = perfis[codigoEstacao] || [0, 0, 0, 0, 0, 0, 0, 0];

  return horas.map((hora, idx) => {
    const delta = variacoes[idx];
    const obs = Number((cotaValida + delta).toFixed(2));
    const prev = Number((obs + (idx > 4 ? -0.01 : 0.01)).toFixed(2));

    return {
      hora,
      cota_observada: Math.max(0.2, obs),
      cota_prevista: Math.max(0.2, prev)
    };
  });
}

function gerarHistorico2026(): HistoryData[] {
  const resultado: HistoryData[] = [];
  const hoje = new Date(2026, 8, 29);

  const cotasObs = [3.8, 3.3, 4.8, 3.9, 3.7, 3.9, 3.6, 3.2, 2.6, 3.0, 2.9, 2.8, 2.7, 2.5, 2.4, 1.6, 2.0, 1.9];
  const cotasPrev = [3.2, 3.1, 3.0, 2.8, 2.6, 2.4, 2.2, 2.1, 2.0, 3.8, 2.8, 3.8, 3.1, 2.6, 2.3, 1.9, 1.8, 1.7];

  for (let i = 17; i >= 0; i--) {
    const d = new Date(hoje);
    d.setDate(d.getDate() - (i * 2));
    const dia = String(d.getDate()).padStart(2, '0');
    const mes = String(d.getMonth() + 1).padStart(2, '0');

    resultado.push({
      data: `${dia}/${mes}`,
      cota_observada: cotasObs[17 - i],
      cota_prevista: cotasPrev[17 - i],
    });
  }
  return resultado;
}

export default function Dashboard() {
  const [estacoes, setEstacoes] = useState<EstacaoData[]>(ESTACOES_11_BACIAS);
  const [history, setHistory] = useState<HistoryData[]>(gerarHistorico2026());
  const [hourlyData, setHourlyData] = useState<HourlyData[]>([]);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [estacaoIndex, setEstacaoIndex] = useState(0);

  // FUNÇÃO DE BUSCA DO CLIMA COM CACHE DE 10 MINUTOS NO LOCALSTORAGE
  async function fetchWeatherForStation(codigo: string) {
    const coords = CIDADE_COORDS[codigo] || CIDADE_COORDS['87450000'];
    const cacheKey = `samh_weather_${codigo}`;
    const agora = Date.now();
    const TEN_MINUTES_MS = 10 * 60 * 1000;

    // 1. Verificar se existem dados em cache válidos (menos de 10 min)
    const cachedData = localStorage.getItem(cacheKey);
    if (cachedData) {
      try {
        const { timestamp, data } = JSON.parse(cachedData);
        if (agora - timestamp < TEN_MINUTES_MS) {
          setWeather(data);
          return;
        }
      } catch (e) {
        console.warn('Cache de clima inválido, buscando atualização...');
      }
    }

    // 2. Se o cache expirou ou não existe, consulta a API do Open-Meteo
    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=America%2FSao_Paulo`
      );

      if (res.ok) {
        const wData = await res.json();
        const newWeatherData: WeatherData = {
          tempCurrent: Math.round(wData.current.temperature_2m),
          humidity: wData.current.relative_humidity_2m,
          wind: Math.round(wData.current.wind_speed_10m),
          rainProb: wData.current.precipitation,
          condition: 'Parcialmente ensolarado',
          cidade: coords.nome
        };

        // Guardar no localStorage com timestamp
        localStorage.setItem(
          cacheKey,
          JSON.stringify({ timestamp: agora, data: newWeatherData })
        );
        setWeather(newWeatherData);
      } else {
        throw new Error(`Open-Meteo respondeu com status ${res.status}`);
      }
    } catch (e) {
      console.warn(`[SAMH Clima] Falha na API para ${coords.nome}. Mantendo fallback/cache antigo:`, e);
      // Fallback em caso de erro 503/rede: usar o último cache disponível ou valores padrão
      if (cachedData) {
        setWeather(JSON.parse(cachedData).data);
      } else {
        setWeather({
          tempCurrent: 20,
          humidity: 60,
          wind: 10,
          rainProb: 0,
          condition: 'Estável (sem dados)',
          cidade: coords.nome
        });
      }
    }
  }

  // BUSCA DADOS REAIS DA API DO NEXT.JS (STATIONS/ROUTE.TS)
// BUSCA DADOS REAIS DA API DO NEXT.JS (STATIONS/ROUTE.TS)
useEffect(() => {
  async function carregarDadosDashboard() {
    try {
      const res = await fetch('/api/v1/stations', { cache: 'no-store' });
      if (res.ok) {
        const estacoesAPI = await res.json();

        if (Array.isArray(estacoesAPI) && estacoesAPI.length > 0) {
          const estacoesFormatadas = estacoesAPI.map((e: any) => {
            const cotaObsRaw = e.cotaObs ?? e.cota_obs ?? e.cota_observada;
            const cotaPrevRaw = e.cotaPrev ?? e.cota_prev ?? e.cota_prevista;

            return {
              ...e,
              cotaObs: typeof cotaObsRaw === 'number' ? cotaObsRaw : (parseFloat(cotaObsRaw) || null),
              cotaPrev: typeof cotaPrevRaw === 'number' ? cotaPrevRaw : (parseFloat(cotaPrevRaw) || null),
            };
          });

          setEstacoes(estacoesFormatadas);
        }
      }
    } catch (err) {
      console.warn("Erro ao carregar /api/v1/stations, mantendo estado local:", err);
    } finally {
      setLoading(false);
    }
  }

  carregarDadosDashboard();
  const interval = setInterval(carregarDadosDashboard, 30000);
  return () => clearInterval(interval);
}, []);

  useEffect(() => {
    if (estacoes.length === 0) return;
    setHourlyData(gerarDadosHoje(estacoes[estacaoIndex].codigo, estacoes[estacaoIndex].cotaObs));
    fetchWeatherForStation(estacoes[estacaoIndex].codigo);

    const interval = setInterval(() => {
      setEstacaoIndex((prev) => {
        const next = (prev + 1) % estacoes.length;
        const est = estacoes[next];
        setHourlyData(gerarDadosHoje(est.codigo, est.cotaObs));
        fetchWeatherForStation(est.codigo);
        return next;
      });
    }, 10000);
    return () => clearInterval(interval);
  }, [estacoes, estacaoIndex]);

  if (loading || estacoes.length === 0) {
    return (
      <div style={{ backgroundColor: '#03120c' }} className="p-8 text-emerald-100 min-h-screen">
        Carregando dados telemétricos das bacias...
      </div>
    );
  }

  const estacaoAtual = estacoes[estacaoIndex];
  const statusAtual = calcularStatus(estacaoAtual);

  const variacaoCm = hourlyData.length > 0
    ? Math.round((hourlyData[hourlyData.length - 1].cota_observada - hourlyData[0].cota_observada) * 100)
    : 0;

  const cardStyle = {
    backgroundColor: '#072017',
    borderColor: '#0e3829'
  };

  return (
    <main style={{ backgroundColor: '#03120c' }} className="min-h-screen text-emerald-50 p-6 flex flex-col justify-between font-sans">
      <div>
        <header className="flex justify-between items-center mb-6 pb-4 border-b border-[#0e3829]">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white">SAMH</h1>
            <p className="text-xs text-emerald-300/60">Sistema Automatizado de Monitoramento Hidrológico</p>
          </div>
          <div style={cardStyle} className="border px-3 py-1 rounded text-xs text-emerald-300">
            Última atualização: {new Date().toLocaleDateString('pt-BR')}
          </div>
        </header>

        <div style={cardStyle} className="mb-6 p-4 rounded-lg border flex items-center gap-3">
          <span className="text-emerald-400 text-xl">✓</span>
          <div>
            <h2 className="font-semibold text-white uppercase tracking-wide">MONITORAMENTO ATIVO</h2>
            <p className="text-xs text-emerald-300/60">Rede hidrometeorológica telemétrica em tempo real.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
          {/* COLUNA ESQUERDA */}
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-3">
              <div style={cardStyle} className="border p-4 rounded-lg flex items-center justify-between">
                <div>
                  <span className="text-lg font-bold tracking-wide text-white block">
                    BACIA {estacaoAtual.nome}: <span className={statusAtual.cor}>{statusAtual.texto}</span>
                  </span>
                  <span className="text-xs text-emerald-300/60">{estacaoAtual.rio}</span>
                </div>
                <span style={{ backgroundColor: '#03120c' }} className="text-xs px-2 py-1 rounded text-emerald-400 border border-[#0e3829] whitespace-nowrap">
                  Rotação 10s
                </span>
              </div>

              <div style={cardStyle} className="border p-4 rounded-lg">
                <p className="text-xs text-emerald-300/60 mb-1">Cota Prevista (24h)</p>
                <p className="text-2xl font-bold text-sky-400 transition-all duration-500">
                  {estacaoAtual.cotaPrev !== null && estacaoAtual.cotaPrev !== undefined
                    ? `${Number(estacaoAtual.cotaPrev).toFixed(2)} m`
                    : 'N/D'}
                </p>
              </div>

              <div style={cardStyle} className="border p-4 rounded-lg">
                <p className="text-xs text-emerald-300/60 mb-1">Cota Observada em Tempo Real</p>
                <p className="text-2xl font-bold text-white transition-all duration-500">
                  {estacaoAtual.cotaObs !== null && estacaoAtual.cotaObs !== undefined
                    ? `${Number(estacaoAtual.cotaObs).toFixed(2)} m`
                    : 'N/D'}
                </p>
              </div>
            </div>

            <div style={cardStyle} className="border p-5 rounded-lg flex-1 flex flex-col justify-between">
              <h3 className="text-md font-semibold mb-4 text-white">Histórico e Tendência (Últimos 30 dias)</h3>
              <div style={{ width: '100%', height: '260px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#0e3829" />
                    <XAxis dataKey="data" stroke="#6ee7b7" fontSize={10} />
                    <YAxis
                      stroke="#6ee7b7"
                      fontSize={10}
                      unit="m"
                      domain={[(dataMin: number) => Math.max(0, Number((dataMin - 0.2).toFixed(2))), (dataMax: number) => Number((dataMax + 0.2).toFixed(2))]}
                    />
                    <Tooltip contentStyle={{ backgroundColor: '#03120c', borderColor: '#0e3829', color: '#fff' }} itemStyle={{ color: '#ecfdf5' }} />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Line type="monotone" dataKey="cota_observada" name="Cota Observada (m)" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3 }} connectNulls />
                    <Line type="monotone" dataKey="cota_prevista" name="Cota Prevista (m)" stroke="#f59e0b" strokeWidth={2} strokeDasharray="4 4" dot={false} connectNulls />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* COLUNA DIREITA */}
          <div className="flex flex-col gap-6">
            <div style={cardStyle} className="border p-6 rounded-lg flex justify-between items-center">
              <div className="flex items-center gap-4">
                <span className="text-6xl">⛅</span>
                <div className="flex items-baseline">
                  <span className="text-6xl font-black text-white">{weather?.tempCurrent ?? 20}</span>
                  <span className="text-sm text-emerald-300/60 ml-2">°C | °F</span>
                </div>
              </div>

              <div className="text-right text-xs text-emerald-200 space-y-1">
                <p className="text-lg font-bold text-white mb-1">Clima em {weather?.cidade ?? 'Porto Alegre'}</p>
                <p>{new Date().toLocaleDateString('pt-BR', { weekday: 'long' })}</p>
                <p className="text-emerald-300">{weather?.condition}</p>
                <p>Chuva: {weather?.rainProb ?? 0}% | Umidade: {weather?.humidity ?? 60}%</p>
                <p>Vento: {weather?.wind ?? 10} km/h</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1 min-h-[280px]">
              {/* PAINEL INFERIOR ESQUERDO: ANÁLISE INTRADIA */}
              <div style={cardStyle} className="border p-5 rounded-lg flex flex-col justify-between h-full">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-xl font-bold text-white tracking-wide">Análise Intradia (Hoje)</h3>
                  <span className="text-sm text-emerald-400 font-mono font-bold tracking-wider">{estacaoAtual.nome}</span>
                </div>

                <div className="w-full flex-1 min-h-[190px] mt-2 flex flex-col justify-between">
                  <ResponsiveContainer width="100%" height="85%">
                    <LineChart data={hourlyData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#0e3829" />
                      <XAxis dataKey="hora" stroke="#6ee7b7" fontSize={9} />
                      <YAxis
                        stroke="#6ee7b7"
                        fontSize={9}
                        unit="m"
                        domain={[
                          (dataMin: number) => Number((dataMin - 0.3).toFixed(2)),
                          (dataMax: number) => Number((dataMax + 0.3).toFixed(2))
                        ]}
                      />
                      <Tooltip contentStyle={{ backgroundColor: '#03120c', borderColor: '#0e3829', color: '#fff' }} itemStyle={{ color: '#ecfdf5' }} />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '2px' }} />
                      <Line type="monotone" dataKey="cota_observada" name="Observada" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="cota_prevista" name="Prevista" stroke="#f59e0b" strokeWidth={2} strokeDasharray="3 3" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>

                  <div className="text-center pt-1">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                      VARIAÇÃO DE {variacaoCm >= 0 ? `+${variacaoCm}` : variacaoCm} CM
                    </span>
                  </div>
                </div>
              </div>

              {/* PAINEL INFERIOR DIREITO: MAPA INTERATIVO DO RS */}
              <div style={cardStyle} className="border rounded-lg p-2 flex items-center justify-center h-full min-h-[240px]">
                <MapaRS
                  estacoes={estacoes}
                  estacaoSelecionadaCodigo={estacaoAtual.codigo}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer className="mt-8 border-t border-[#0e3829] pt-4 text-center">
        <p className="text-xs text-emerald-500/60">
          Desenvolvido por <span className="text-emerald-300 font-medium">Laudecir Jr. Cardoso</span> | SAMH — {new Date().getFullYear()}
        </p>
      </footer>
    </main>
  );
}