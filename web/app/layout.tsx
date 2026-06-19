import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Systematic Alpha Research Lab — Does this signal survive reality?",
  description:
    "A signal survival lab: testing whether five explainable systematic trading signals survive transaction costs, out-of-sample validation, and market stress on 20 years of real ETF data.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700&family=Red+Hat+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
