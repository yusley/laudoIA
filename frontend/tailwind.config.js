/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#141214",
        sand: "#f4efe5",
        ember: "#d56a3a",
        moss: "#7a8f62",
        brass: "#c9a55a"
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["Segoe UI", "sans-serif"]
      },
      boxShadow: {
        panel: "0 20px 60px rgba(0,0,0,0.18)"
      }
    },
  },
  plugins: [],
};
