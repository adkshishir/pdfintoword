import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: "#2563EB",
        cta: "#3B82F6",
        success: "#16A34A",
      },
    },
  },
  plugins: [],
};

export default config;
