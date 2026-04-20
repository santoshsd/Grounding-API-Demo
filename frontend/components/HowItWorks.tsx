"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "grounding-howto-collapsed";

export function HowItWorks() {
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setCollapsed(localStorage.getItem(STORAGE_KEY) === "1");
    }
  }, []);

  function toggle() {
    const next = !collapsed;
    setCollapsed(next);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, next ? "1" : "0");
    }
  }

  return (
    <section className="border border-[var(--border)] bg-[var(--panel)] rounded-lg p-4 text-sm leading-relaxed">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-semibold text-base">How this dashboard works</h2>
        <button
          onClick={toggle}
          className="text-xs text-[var(--muted)] hover:text-[var(--fg)] border border-[var(--border)] rounded px-2 py-0.5"
          type="button"
        >
          {collapsed ? "Show" : "Hide"}
        </button>
      </div>

      {!collapsed && (
        <div className="mt-3 flex flex-col gap-3 text-[var(--muted)]">
          <p>
            <span className="text-[var(--fg)] font-semibold">Compare providers side by side.</span>{" "}
            Check one or more providers, hit <span className="text-[var(--fg)]">Run query</span>,
            and every provider runs the same question twice — once with its grounding tool on
            (web search, retrieval, etc.) and once without, so you can see the delta. Providers
            fall into two shapes: <em>direct web-search APIs</em> (Claude, OpenAI, Gemini call
            search inside their own model) and <em>retrieval + synthesis</em> (Exa and Tavily
            fetch search results that Gemini then turns into a grounded answer). Perplexity and
            Brave are wired up in the backend but hidden in the UI for now.
          </p>

          <div>
            <p>
              <span className="text-[var(--fg)] font-semibold">LLM-as-judge scoring.</span> After
              each run, a separate LLM reads every answer and its citations, then scores three
              dimensions from <span className="text-[var(--fg)]">1 (poor) to 5 (excellent)</span>:
            </p>
            <ul className="list-disc list-inside space-y-0.5 ml-2 mt-1">
              <li>
                <span className="text-[var(--fg)]">Cor — Correctness</span>: factual accuracy of
                the answer.
              </li>
              <li>
                <span className="text-[var(--fg)]">Grd — Groundedness</span>: whether the answer
                sticks to what the citations actually say rather than speculating.
              </li>
              <li>
                <span className="text-[var(--fg)]">Cit — Citation support</span>: whether the
                cited sources genuinely back the claims.
              </li>
            </ul>
            <p className="mt-1">
              Pills are colored green (≥4), grey (3), or red (≤2). Hover any pill for the full
              tooltip. The judge runs <span className="text-[var(--fg)]">grounded itself</span> —
              it does a web search to verify time-sensitive facts before scoring, which avoids
              the &ldquo;training cutoff thinks the answer is wrong&rdquo; trap.
            </p>
          </div>

          <p>
            <span className="text-[var(--fg)] font-semibold">Choose your judge.</span> The{" "}
            <span className="text-[var(--fg)]">Judge</span> dropdown lets you switch between
            Gemini (<code>gemini-3-pro-preview</code>) and Claude (
            <code>claude-sonnet-4-6</code>). Different judges have different biases; running the
            same query with both is a quick way to see where they disagree. The chosen judge is
            shown on every response card as <em>&ldquo;judged by X · model&rdquo;</em>.
          </p>

          <div>
            <p>
              <span className="text-[var(--fg)] font-semibold">What each card shows.</span> For
              every (provider, grounded/baseline) pair you get:
            </p>
            <ul className="list-disc list-inside space-y-0.5 ml-2 mt-1">
              <li>The answer text.</li>
              <li>The exact citations returned (URL, title, domain).</li>
              <li>Latency, input/output tokens, and a USD cost estimate.</li>
              <li>The three judge scores plus a one-line rationale.</li>
              <li>
                Which answer model produced it (top-right) and which judge scored it (next to the
                pills).
              </li>
            </ul>
          </div>

          <p className="text-xs">
            Head to <span className="text-[var(--fg)]">Compare</span> for aggregate charts across
            all past runs, or click any run in the{" "}
            <span className="text-[var(--fg)]">Recent runs</span> sidebar to revisit it.
          </p>
        </div>
      )}
    </section>
  );
}
