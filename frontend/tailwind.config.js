/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        purple: {
          brand: 'rgba(88, 86, 214, 1)',
          deep: 'rgba(103, 58, 183, 1)',
        },
        kpi: {
          blue: '#3b82f6',
          green: '#22c55e',
          orange: '#f97316',
          purple: '#8b5cf6',
        }
      },
      backgroundImage: {
        'gradient-header': 'linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%)',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
      }
    },
  },
  plugins: [],
}
