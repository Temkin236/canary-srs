/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#FAF8F5',
        surface: '#FFFFFF',
        'surface-elevated': '#F4EFEA',
        charcoal: {
          DEFAULT: '#1C1917',
          light: '#44403C',
          muted: '#78716C',
        },
        accent: {
          DEFAULT: '#B8860B',
          light: '#D4AF37',
          dark: '#996515',
        },
        border: '#E7E5E4',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        serif: ['Newsreader', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
