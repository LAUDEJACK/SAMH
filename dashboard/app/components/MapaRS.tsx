'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Estacao {
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

interface MapaRSProps {
  estacoes: Estacao[];
  estacaoSelecionadaCodigo?: string;
}

// Centro Geográfico do Rio Grande do Sul
const CENTRO_RS: [number, number] = [-30.0, -53.5];

// Animação CSS para o efeito de pulso nos alertas do geoprocessamento
const pulseStyles = `
  @keyframes pulseGlow {
    0% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(var(--marker-rgb), 0.8);
    }
    70% {
      transform: scale(1.18);
      box-shadow: 0 0 0 12px rgba(var(--marker-rgb), 0);
    }
    100% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(var(--marker-rgb), 0);
    }
  }
  .animate-pulse-glow {
    animation: pulseGlow 1.8s infinite ease-in-out;
  }
`;

// Componente para travar a câmera no centro do estado do RS
function CentralizarMapaRS() {
  const map = useMap();
  useEffect(() => {
    if (map) {
      map.setView(CENTRO_RS, 6.2);
    }
  }, [map]);
  return null;
}

// Função para gerar marcador colorido e pulsante de acordo com o status hidráulico
function criarIconeMarcador(est: Estacao, selecionada: boolean) {
  let corHex = '#10b981'; // Emerald (Normal)
  let rgbValues = '16, 185, 129';

  if (est.cotaObs === null || est.cotaObs === undefined) {
    corHex = '#9ca3af'; // Cinza (Sem sinal)
    rgbValues = '156, 163, 175';
  } else if (est.cotaObs >= est.cotaInundacao) {
    corHex = '#ef4444'; // Vermelho (Inundação)
    rgbValues = '239, 68, 68';
  } else if (est.cotaObs >= est.cotaAlerta) {
    corHex = '#f97316'; // Laranja (Alerta)
    rgbValues = '249, 115, 22';
  } else if (est.cotaObs < 1.0) {
    corHex = '#f59e0b'; // Âmbar (Nível baixo)
    rgbValues = '245, 158, 11';
  }

  // Define se o marcador deve pulsar (estação ativa em foco ou em estado de Alerta/Inundação)
  const estaEmAlerta = est.cotaObs !== null && est.cotaObs >= est.cotaAlerta;
  const devePulsar = selecionada || estaEmAlerta;

  const tamanho = selecionada ? 20 : 14;
  const borda = selecionada ? '2.5px solid #ffffff' : '1.5px solid #03120c';

  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `
      <style>${pulseStyles}</style>
      <div 
        class="${devePulsar ? 'animate-pulse-glow' : ''}" 
        style="
          --marker-rgb: ${rgbValues};
          background-color: ${corHex};
          width: ${tamanho}px;
          height: ${tamanho}px;
          border-radius: 50%;
          border: ${borda};
          box-shadow: 0 0 10px ${corHex};
          transition: all 0.3s ease;
        "
      ></div>
    `,
    iconSize: [tamanho, tamanho],
    iconAnchor: [tamanho / 2, tamanho / 2],
  });
}

export default function MapaRS({ estacoes, estacaoSelecionadaCodigo }: MapaRSProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div className="w-full h-full min-h-[220px] bg-[#072017] flex items-center justify-center text-emerald-400/50 text-xs rounded-lg">
        Iniciando Geoprocessamento do RS...
      </div>
    );
  }

  return (
    <div className="w-full h-full min-h-[220px] rounded-lg overflow-hidden relative border border-[#0e3829]">
      <MapContainer
        center={CENTRO_RS}
        zoom={6.2}
        scrollWheelZoom={false}
        style={{ width: '100%', height: '100%', minHeight: '220px', backgroundColor: '#03120c' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <CentralizarMapaRS />

        {estacoes.map((est) => {
          const isSelected = est.codigo === estacaoSelecionadaCodigo;
          return (
            <Marker
              key={est.codigo}
              position={[est.lat, est.lon]}
              icon={criarIconeMarcador(est, isSelected)}
            >
              <Popup>
                <div className="p-1 text-slate-900 font-sans">
                  <strong className="block text-sm">{est.nome}</strong>
                  <span className="text-xs text-slate-600 block mb-1">{est.rio}</span>
                  <div className="text-xs font-semibold">
                    Cota Obs: {est.cotaObs !== null ? `${est.cotaObs.toFixed(2)}m` : 'N/D'}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}