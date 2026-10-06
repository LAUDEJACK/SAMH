<div align="center">

# 🌊 SAMH — Sistema Automatizado de Monitoramento Hidrológico

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge)](#)
[![Location](https://img.shields.io/badge/Regi%C3%A3o-Rio%20Grande%20do%20Sul%20%2F%20Brasil-green?style=for-the-badge&logo=googlemaps&logoColor=white)](#)

<p align="center">
  <b>Plataforma telemétrica e preditiva em tempo real para monitoramento de bacias hidrográficas e alerta antecipado de inundações no Estado do Rio Grande do Sul.</b>
</p>

</div>

---

> **Plataforma telemétrica e preditiva em tempo real para monitoramento de bacias hidrográficas e alerta antecipado de inundações no Estado do Rio Grande do Sul.**

---

## 🌊 Sobre o Projeto

O **SAMH** foi desenvolvido com o propósito de integrar dados telemétricos das redes oficiais de monitoramento hidrometeorológico da **ANA (Agência Nacional de Águas e Saneamento Básico)** e do **SGB/CPRM**, fornecendo visualização geoespacial interativa, alertas automatizados de cotas críticas (Alerta / Inundação) e modelagem preditiva de tendência de nível de rios.

### 🛠️ Principais Recursos

- **Geoprocessamento Interativo (RS):** Mapeamento dinâmico das estações telemétricas no Rio Grande do Sul com indicativos visuais em tempo real.
- **Alertas Telemétricos e Status em Pulso:** Efeito visual dinâmico (*Glow Pulse*) para rápido reconhecimento visual de bacias em cota de emergência.
- **Integração telemétrica direta com APIs da ANA:** Leitura e sanitização contínua de dados telemétricos via rotas otimizadas.
- **Histórico e Tendência Intradia:** Gráficos interativos para análise temporal contínua das variações dos níveis fluviais.
- **Design Dashboard Dark Mode High-Contrast:** Interface minimalista otimizada para centros de operação e monitoramento.

---

## 🚀 Arquitetura e Tecnologias

- **Frontend:** [Next.js 14+](https://nextjs.org/) (App Router, React, TypeScript, Tailwind CSS)
- **Geoprocessamento:** [Leaflet](https://leafletjs.org/) / `react-leaflet`
- **Backend / API:** Next.js Route Handlers + FastAPI (Python integration)
- **Análise de Dados:** Python (Pandas, NumPy, Scikit-Learn / XGBoost)

---

## 🔧 Como Executar o Projeto

### Pré-requisitos
- Node.js (v18+ recomendado)
- Python 3.10+ (para o pipeline backend/modelo preditivo)

### Passos para execução do Dashboard Next.js:

```bash
# Entre no diretório do dashboard
cd dashboard

# Instale as dependências
npm install

# Execute o servidor de desenvolvimento
npm run dev
```
🧑‍💻 Desenvolvido por Laudecir Jr. Cardoso 