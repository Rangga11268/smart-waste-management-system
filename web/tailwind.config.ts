import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecfdf5',
          500: '#10b981',
          600: '#059669', // Eco-Tech Brand Primary
          700: '#047857',
          900: '#064e3b',
        },
        'primary-50': '#ecfdf5',
        'primary-500': '#10b981',
        'primary-600': '#059669',
        'primary-700': '#047857',
        'primary-900': '#064e3b',
        'surface-ground': '#f8fafc',
        'surface-card': '#ffffff',
        'border-subtle': '#e2e8f0',
        'text-muted': '#64748b',
        'text-body': '#334155',
        'text-heading': '#0f172a',
        surface: {
          ground: '#f8fafc',
          card: '#ffffff',
        },
        border: {
          subtle: '#e2e8f0',
        },
        text: {
          muted: '#64748b',
          body: '#334155',
          heading: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'var(--font-inter)', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Arial', 'sans-serif'],
        heading: ['Inter', 'var(--font-inter)', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Arial', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
