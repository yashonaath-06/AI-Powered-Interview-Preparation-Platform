import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eef4ff",
          100: "#dbe7ff",
          200: "#bbd0ff",
          300: "#8eb0ff",
          400: "#5e87ff",
          500: "#3a64ff",
          600: "#2745f5",
          700: "#2034dc",
          800: "#1f2db1",
          900: "#1f2c8b",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "hero-grid":
          "linear-gradient(to right, rgba(120,120,160,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(120,120,160,0.08) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
