# SAMH — Sistema Automatizado de Monitoramento Hidrológico

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