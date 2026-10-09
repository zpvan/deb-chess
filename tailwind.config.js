/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: "var(--primary)",
        "on-primary": "var(--on-primary)",
        "primary-container": "var(--primary-container)",
        "on-primary-container": "var(--on-primary-container)",
        surface: "var(--surface)",
        "surface-container": "var(--surface-container)",
        "on-surface": "var(--on-surface)",
        "on-surface-variant": "var(--on-surface-variant)",
        "outline-variant": "var(--outline-variant)",
        "success-container": "var(--success-container)",
        "on-success-container": "var(--on-success-container)",
        "error-container": "var(--error-container)",
        "on-error-container": "var(--on-error-container)",
        star: "var(--star)",
        "hint-container": "var(--hint-container)",
        "on-hint-container": "var(--on-hint-container)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
