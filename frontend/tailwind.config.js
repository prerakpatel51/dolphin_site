export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ocean: { 50: "#eef9fd", 100: "#d3eff8", 200: "#a3dfef",
                 300: "#5fc7e2", 400: "#28a8ce", 500: "#1389b1",
                 600: "#106e92", 700: "#0f5876", 800: "#11475f",
                 900: "#0b3a52", 950: "#062436" },
        sand: { 50: "#fdf8ee", 100: "#f7e7c4", 200: "#f0d291" },
      },
      fontFamily: { display: ["Fraunces", "ui-serif", "serif"], sans: ["Inter", "ui-sans-serif"] },
    },
  },
  plugins: [],
};
