/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Glacier — Glassmorphism 冰蓝低调配色
        background: "#0a0e1a",
        surface: "#0f1524",
        "surface-dim": "#0f1524",
        "surface-bright": "#1a2438",
        "surface-container": "#141c2e",
        "surface-container-low": "#111828",
        "surface-container-lowest": "#0a0e1a",
        "surface-container-high": "#1a2438",
        "surface-container-highest": "#202c42",
        "surface-variant": "#1a2438",
        "surface-tint": "#7dd3fc",
        "on-surface": "#e0e8f0",
        "on-surface-variant": "#a0b4c4",
        "on-background": "#e0e8f0",
        // Primary: Ice-blue
        primary: "#7dd3fc",
        "primary-container": "#0e4d6e",
        "on-primary": "#001f2e",
        "on-primary-container": "#c8eaff",
        "primary-fixed": "#c8eaff",
        "primary-fixed-dim": "#7dd3fc",
        "on-primary-fixed": "#001f2e",
        "on-primary-fixed-variant": "#004d73",
        "inverse-primary": "#0a4c6e",
        // Secondary: Muted steel-blue
        secondary: "#88b4cc",
        "secondary-container": "#1a3a4e",
        "on-secondary": "#001f2e",
        "on-secondary-container": "#c0d8e8",
        "secondary-fixed": "#c0d8e8",
        "secondary-fixed-dim": "#88b4cc",
        "on-secondary-fixed": "#0d1f2b",
        "on-secondary-fixed-variant": "#2a4a5e",
        // Tertiary: Soft lavender
        tertiary: "#c8a0f0",
        "tertiary-container": "#3d2060",
        "on-tertiary": "#1a002e",
        "on-tertiary-container": "#e8d0ff",
        "tertiary-fixed": "#e8d0ff",
        "tertiary-fixed-dim": "#c8a0f0",
        "on-tertiary-fixed": "#1a002e",
        "on-tertiary-fixed-variant": "#4d2a73",
        // Error: Soft coral
        error: "#ff6b6b",
        "error-container": "#3d1414",
        "on-error": "#1a0000",
        "on-error-container": "#ffb3b3",
        // Outline
        outline: "#4a6070",
        "outline-variant": "#2a3a48",
        "inverse-surface": "#e0e8f0",
        "inverse-on-surface": "#0a0e1a",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px",
      },
    },
  },
  plugins: [],
}
