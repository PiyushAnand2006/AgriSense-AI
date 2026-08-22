import type { Config } from "tailwindcss";

/**
 * AgriSense AI design tokens.
 * Earth/nature-inspired primary green, harvest amber accent, warm neutral soil.
 */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f1faf3",
          100: "#ddf2e2",
          200: "#bce5cb",
          300: "#8dd1a8",
          400: "#57b57d",
          500: "#339961",
          600: "#247b4c",
          700: "#1e633e",
          800: "#1b4f34",
          900: "#17412c",
          950: "#0a2417",
        },
        accent: {
          50: "#fffaeb",
          100: "#fef0c7",
          200: "#fee08a",
          300: "#fdca4d",
          400: "#fcb424",
          500: "#f5930b",
          600: "#d96f06",
          700: "#b44e09",
          800: "#923d0e",
          900: "#78330f",
        },
        soil: {
          50: "#faf9f7",
          100: "#f1efeb",
          200: "#e5e1d9",
          300: "#d2cabd",
          400: "#b7ab98",
          500: "#9d8f7b",
          600: "#847564",
          700: "#6c5f53",
          800: "#584e45",
          900: "#4a423b",
          950: "#292420",
        },
      },
      fontFamily: {
        display: ["Manrope", "Inter", "system-ui", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16, 24, 40, 0.04), 0 8px 24px -8px rgba(16, 24, 40, 0.12)",
        "card-hover": "0 2px 4px rgba(16, 24, 40, 0.06), 0 16px 32px -12px rgba(16, 24, 40, 0.18)",
        glow: "0 0 0 4px rgba(51, 153, 97, 0.15)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.5s ease-out both",
        "fade-in": "fade-in 0.4s ease-out both",
      },
    },
  },
  plugins: [],
} satisfies Config;
