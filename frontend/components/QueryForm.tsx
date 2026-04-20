"use client";

import { useEffect, useState } from "react";
import {
  getJudgeConfig,
  listProviders,
  type JudgeConfig,
  type JudgeOption,
} from "@/lib/api";

export type QueryFormValue = {
  query: string;
  providers: string[];
  include_ungrounded: boolean;
  run_judge: boolean;
  judge_provider?: "google" | "anthropic";
};

const EXAMPLES = [
  "Who won the 2025 Nobel Prize in Physics?",
  "What happened at the last Fed meeting?",
  "Current stock price of NVIDIA and key news this week.",
  "What are the top AI research papers published this month?",
  "Who won Best Picture at the 2026 Academy Awards?",
  "Latest NBA playoff standings and top scorers this week.",
  "Who won the 2026 Super Bowl and by what score?",
  "Latest GPT-5 release details and benchmark results.",
  "Most recent Apple product announcements in 2026.",
  "What are the most significant geopolitical events this month?",
  "Current status of the US-China tariff negotiations.",
  "Top-grossing movies at the box office this weekend.",
];

// Providers configured on the backend but hidden from the UI for now.
// Re-enable by removing from this set. See README "Hidden providers" note.
const HIDDEN_PROVIDERS = new Set(["perplexity", "brave"]);

// Providers checked by default when the UI loads.
const DEFAULT_SELECTED = new Set(["claude", "openai_ws", "exa"]);

export function QueryForm({
  onSubmit,
  loading,
}: {
  onSubmit: (v: QueryFormValue) => void;
  loading: boolean;
}) {
  const [query, setQuery] = useState("");
  const [providers, setProviders] = useState<string[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [includeUngrounded, setIncludeUngrounded] = useState(true);
  const [runJudge, setRunJudge] = useState(true);
  const [judgeCfg, setJudgeCfg] = useState<JudgeConfig | null>(null);
  const [judge, setJudge] = useState<JudgeOption["id"] | null>(null);

  useEffect(() => {
    listProviders()
      .then((p) => {
        const visible = p.filter((x) => !HIDDEN_PROVIDERS.has(x));
        setProviders(visible);
        setSelected(new Set(visible.filter((x) => DEFAULT_SELECTED.has(x))));
      })
      .catch(() => setProviders([]));
    getJudgeConfig()
      .then((c) => {
        setJudgeCfg(c);
        setJudge(c.default);
      })
      .catch(() => setJudgeCfg(null));
  }, []);

  function toggle(p: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(p) ? next.delete(p) : next.add(p);
      return next;
    });
  }

  function submit() {
    if (!query.trim() || selected.size === 0) return;
    onSubmit({
      query: query.trim(),
      providers: [...selected],
      include_ungrounded: includeUngrounded,
      run_judge: runJudge,
      judge_provider: judge ?? undefined,
    });
  }

  return (
    <div className="flex flex-col gap-4">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question where grounding matters (freshness, niche facts, verifiable claims)…"
        className="w-full border border-[var(--border)] bg-[var(--panel)] rounded-lg p-3 min-h-[100px] text-sm"
      />

      <div className="flex flex-wrap gap-2">
        {EXAMPLES.map((e) => (
          <button
            key={e}
            onClick={() => setQuery(e)}
            className="text-xs px-2 py-1 border border-[var(--border)] rounded hover:bg-[var(--panel)]"
            type="button"
          >
            {e}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        <span className="text-sm text-[var(--muted)]">Providers:</span>
        {providers.map((p) => (
          <label key={p} className="flex items-center gap-1 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={selected.has(p)}
              onChange={() => toggle(p)}
            />
            {p}
          </label>
        ))}
      </div>

      <div className="flex flex-wrap gap-4 items-center">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={includeUngrounded}
            onChange={(e) => setIncludeUngrounded(e.target.checked)}
          />
          Include ungrounded baseline
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={runJudge}
            onChange={(e) => setRunJudge(e.target.checked)}
          />
          Run LLM judge
        </label>

        {runJudge && judgeCfg && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-[var(--muted)]">Judge:</span>
            <select
              value={judge ?? judgeCfg.default}
              onChange={(e) => setJudge(e.target.value as JudgeOption["id"])}
              className="bg-[var(--panel)] border border-[var(--border)] rounded px-2 py-1 text-sm"
            >
              {judgeCfg.options.map((o) => (
                <option key={o.id} value={o.id} disabled={!o.available}>
                  {o.label} ({o.model}){o.available ? "" : " — no key"}
                </option>
              ))}
            </select>
          </div>
        )}

        <button
          onClick={submit}
          disabled={loading || !query.trim() || selected.size === 0}
          className="ml-auto px-4 py-2 bg-[var(--accent)] text-[var(--bg)] rounded font-semibold text-sm disabled:opacity-50"
        >
          {loading ? "Running…" : "Run query"}
        </button>
      </div>
    </div>
  );
}
