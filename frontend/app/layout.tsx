import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Grounding API Comparison",
  description: "Side-by-side comparison of grounding-capable LLM APIs.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b border-[var(--border)] px-6 py-4 flex items-center justify-between">
          <Link href="/" className="font-semibold text-lg">
            Grounding API Comparison
          </Link>
          <nav className="flex gap-4 text-sm text-[var(--muted)]">
            <Link href="/" className="hover:text-[var(--fg)]">Run</Link>
            <Link href="/compare" className="hover:text-[var(--fg)]">Compare</Link>
          </nav>
        </header>
        <main className="p-6 max-w-[1400px] mx-auto">{children}</main>
      </body>
    </html>
  );
}
