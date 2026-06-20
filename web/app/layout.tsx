import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Systematic Alpha Research Lab · Signal Validation Report",
  description:
    "An institutional-style validation review of five systematic trading signals, tested against transaction costs, out-of-sample data, parameter robustness, and market stress on twenty years of real ETF data. Research only, not investment advice.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Chivo:wght@400;500;600;700;900&family=Fira+Sans:wght@400;500;600;700&family=Fira+Mono:wght@400;500;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
