import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Systematic Alpha Research Lab — Signal Validation Report",
  description:
    "An institutional-style validation review of five systematic trading signals, tested against transaction costs, out-of-sample data, parameter robustness, and market stress on twenty years of real ETF data. Research only — not investment advice.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Libre+Franklin:wght@400;450;500;600;700&family=Source+Code+Pro:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
