import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  weight: ['400', '500', '600', '700', '800'],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'SWMS - Smart Waste Management System',
  description: 'Smart Waste Management System (SWMS) - Eco-Tech Web Dashboard for Urban Sustainability',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="id"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
    >
      <body className={`${inter.className} min-h-screen bg-slate-50 text-slate-800 antialiased selection:bg-emerald-600 selection:text-white`}>
        {children}
      </body>
    </html>
  );
}
