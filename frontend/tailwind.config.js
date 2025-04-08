/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{html,js,hbs}",
  ],
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 