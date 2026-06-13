/** @type {import('tailwindcss').Config} */
module.exports = {
  corePlugins: { preflight: false },
  content: ['./src/**/*.{js,jsx,ts,tsx}', './docs/**/*.{md,mdx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        primary: '#1B7F5A',
        'primary-dark': '#0F5B3A',
        'primary-light': '#3DBF86',
        gold: '#C9A227',
        'gold-dark': '#A8861F',
        'gold-light': '#DFC15A',
        sand: '#F7F3E8',
        'cg-bg': '#0B140F',
        'cg-surface': '#10211A',
        'cg-surface2': '#14271D',
        'cg-border': '#1C3B2C',
        'cg-border2': '#2A5340',
        'cg-text': '#EAF2EC',
        'cg-muted': '#9DB3A6',
        'cg-code': '#0A140E',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'ui-monospace', 'monospace'],
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #3DBF86, #C9A227)',
        'brand-gradient-hover': 'linear-gradient(135deg, #1B7F5A, #A8861F)',
        'hero-glow': 'radial-gradient(circle at 30% 50%, rgba(27,127,90,0.16) 0%, transparent 55%), radial-gradient(circle at 70% 50%, rgba(201,162,39,0.08) 0%, transparent 55%)',
        'card-shine': 'linear-gradient(135deg, rgba(27,127,90,0.06), rgba(201,162,39,0.03))',
      },
      boxShadow: {
        'glow-emerald': '0 0 30px rgba(27,127,90,0.22)',
        'glow-gold': '0 0 30px rgba(201,162,39,0.15)',
        'card': '0 4px 20px rgba(0,0,0,0.4)',
        'card-hover': '0 8px 32px rgba(27,127,90,0.22)',
      },
      borderRadius: {
        pill: '100px',
      },
    },
  },
  plugins: [],
};
