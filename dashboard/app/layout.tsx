import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SAMH - Sistema Automatizado de Monitoramento Hidrológico',
  description: 'Monitoramento e previsão hidrológica em tempo real',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-[#020b08] antialiased">
        {children}
      </body>
    </html>
  );
}