"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AboutGrounding } from "@/components/AboutGrounding";
import { HowItWorks } from "@/components/HowItWorks";
import { JudgeLegend } from "@/components/JudgeLegend";
import { QueryForm, QueryFormValue } from "@/components/QueryForm";
import { ResultsGrid } from "@/components/ResultsGrid";
import { listRuns, runQuery, type Run } from "@/lib/api";

export default function HomePage() {
  const [run, setRun] = useState<Run | null>(null);
  const [history, setHistory] = useState<Run[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refreshHistory() {
    try {
      setHistory(await listRuns());
    } catch {
      /* ignore */
    }
  }

  useEffect(() => {
    refreshHistory();
  }, []);

  async function onSubmit(v: QueryFormValue) {
    setLoading(true);
    setError(null);
    try {
      const r = await runQuery(v);
      setRun(r);
      refreshHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-[1fr_240px] gap-6">
      <div className="flex flex-col gap-6">
        <AboutGrounding />
        <HowItWorks />
        <QueryForm onSubmit={onSubmit} loading={loading} />
        {error && <p className="text-[var(--bad)] text-sm">{error}</p>}
        {run && (
          <>
            <h2 className="text-sm text-[var(--muted)]">
              Run #{run.id} — &ldquo;{run.query}&rdquo;
            </h2>
            <JudgeLegend />
            <ResultsGrid run={run} />
          </>
        )}
      </div>
      <aside className="border-l border-[var(--border)] pl-4 text-sm">
        <h3 className="font-semibold mb-2">Recent runs</h3>
        <ul className="space-y-1">
          {history.map((r) => (
            <li key={r.id}>
              <Link
                href={`/runs/${r.id}`}
                className="text-[var(--muted)] hover:text-[var(--fg)] block truncate"
                title={r.query}
              >
                #{r.id} {r.query}
              </Link>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
