import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0E1520",
          card: "#1B2432",
          border: "#2A3444",
        },
        paper: {
          DEFAULT: "#F7F5F0",
          shadow: "#E8E4DA",
          card: "#FFFFFF",
        },
        highlighter: {
          DEFAULT: "#F5B942",
          soft: "#FCE7B8",
          dark: "#C98F1F",
        },
        sage: {
          DEFAULT: "#6FA287",
          soft: "#DCEAE2",
          dark: "#4C7A61",
        },
        danger: {
          DEFAULT: "#C2493D",
          soft: "#F4DEDB",
        },
        sky: {
          DEFAULT: "#5B8DBE",
          soft: "#DCE8F2",
          dark: "#3D6D9C",
        },
        violet: {
          DEFAULT: "#7C6FCF",
          soft: "#E8E4F7",
          dark: "#5C4FAE",
        },
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        sheet: "3px",
        card: "10px",
      },
      boxShadow: {
        paper: "0 1px 2px rgba(14, 21, 32, 0.06), 0 8px 24px -12px rgba(14, 21, 32, 0.18)",
        lift: "0 12px 32px -8px rgba(14, 21, 32, 0.35)",
      },
      keyframes: {
        "highlight-sweep": {
          "0%": { width: "0%" },
          "100%": { width: "100%" },
        },
        "pin-in": {
          "0%": { opacity: "0", transform: "translateY(6px) scale(0.9)" },
          "100%": { opacity: "1", transform: "translateY(0) scale(1)" },
        },
        "card-slide-in": {
          "0%": { opacity: "0", transform: "translateX(12px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
      },
      animation: {
        "highlight-sweep": "highlight-sweep 0.9s ease-out forwards",
        "pin-in": "pin-in 0.4s ease-out 0.8s forwards",
        "card-slide-in": "card-slide-in 0.5s ease-out 1s forwards",
      },
    },
  },
  plugins: [],
};

export default config;
