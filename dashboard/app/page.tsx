'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, Activity, CloudRain, CheckCircle, RefreshCw } from 'lucide-react';

interface ForecastData {
  data_referencia: string;
  estacao: string;
  cota_observada_m: number;
  cota_prevista_m: number;
  status_alerta: string;
}

export default function Home() {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(false);
    try {
      // Chama o proxy do Next.js configurado no next.config.ts
      const res = await fetch('/api/v1/forecast/latest', { cache: 'no-store' });
      if (!res.ok) throw new Error('Falha na resposta da API');
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error('Erro de conexão com FastAPI:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="flex items-center gap-3">
          <RefreshCw className="h-6 w-6 animate-spin text-blue-400" />
          <p className="text-lg font-medium text-slate-300">Carregando telemetria em tempo real...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 text-white p-4">
        <AlertTriangle className="h-12 w-12 text-amber-500 mb-4" />
        <h2 className="text-xl font-bold mb-2">Servidor de Inferência Indisponível</h2>
        <p className="text-sm text-slate-400 mb-6 text-center max-w-md">
          Certifique-se de que a API FastAPI está em execução no terminal (`uvicorn api.main:app --reload`).
        </p>
        <button
          onClick={fetchData}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium hover:bg-blue-500 transition-colors"
        >
          <RefreshCw className="h-4 w-4" /> Tentar Novamente
        </button>
      </div>
    );
  }

  const isAlert = data.status_alerta !== 'Normal';

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-blue-400">SIPH Dashboard</h1>
          <p className="text-sm text-slate-400">Sistema de Previsão Hidrológica — {data.estacao}</p>
        </div>
        <span className="rounded-full bg-slate-900 px-3 py-1 text-xs text-slate-300 border border-slate-800">
          Última atualização: {data.data_referencia}
        </span>
      </header>

      {/* Status de Alerta */}
      <div className={`mb-8 rounded-xl border p-6 ${isAlert ? 'border-red-500/30 bg-red-950/20' : 'border-emerald-500/30 bg-emerald-950/20'}`}>
        <div className="flex items-center gap-3">
          {isAlert ? <AlertTriangle className="h-8 w-8 text-red-400" /> : <CheckCircle className="h-8 w-8 text-emerald-400" />}
          <div>
            <h2 className="text-xl font-semibold">{data.status_alerta}</h2>
            <p className="text-sm text-slate-400">Monitoramento em tempo real do nível do rio.</p>
          </div>
        </div>
      </div>

      {/* Grid de Métricas */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center gap-2 text-slate-400">
            <Activity className="h-5 w-5 text-blue-400" />
            <span className="text-sm font-medium">Cota Observada</span>
          </div>
          <p className="mt-4 text-4xl font-extrabold text-white">
            {data.cota_observada_m} <span className="text-xl font-normal text-slate-400">m</span>
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center gap-2 text-slate-400">
            <CloudRain className="h-5 w-5 text-indigo-400" />
            <span className="text-sm font-medium">Cota Prevista (24h)</span>
          </div>
          <p className="mt-4 text-4xl font-extrabold text-blue-400">
            {data.cota_prevista_m} <span className="text-xl font-normal text-slate-400">m</span>
          </p>
        </div>
      </div>
    </main>
  );
}