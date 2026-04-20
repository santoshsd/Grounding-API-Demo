"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "grounding-about-collapsed";

export function AboutGrounding() {
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
        <h2 className="font-semibold text-base">What is a Grounding API?</h2>
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
            Large language models answer from their training data — which is frozen in time and
            can{" "}
            <span className="text-[var(--fg)]">hallucinate plausible-sounding facts</span>. A{" "}
            <span className="text-[var(--fg)]">Grounding API</span> connects the model to a live
            information source (web search, a curated index, or your own documents) so it can cite
            real sources, stay current on recent events, and admit when it doesn&rsquo;t know.
          </p>

          <p>
            For AI agents this matters even more: an agent that decides which tool to call, what
            email to send, or what code to ship needs facts it can trust. Grounding is the
            difference between{" "}
            <span className="text-[var(--fg)]">&ldquo;the CEO is probably X&rdquo;</span> and{" "}
            <span className="text-[var(--fg)]">&ldquo;the CEO is Y — here&rsquo;s the source&rdquo;</span>.
          </p>

          <div>
            <p className="mb-1">This dashboard:</p>
            <ul className="list-disc list-inside space-y-0.5 ml-2">
              <li>Fans the same question out to multiple grounding-capable providers at once.</li>
              <li>
                Runs each model twice — <em>grounded</em> (with web/search tools) and a{" "}
                <em>baseline</em> (no tools) — so you can see the delta.
              </li>
              <li>
                Uses an LLM-as-judge to score every response 1–5 on correctness, groundedness, and
                citation support.
              </li>
              <li>
                Reports latency, tokens, cost, and the exact citations each provider returned.
              </li>
            </ul>
          </div>

          <p className="text-xs">
            Try a freshness-sensitive question from the buttons below — the gap between grounded
            and baseline is usually dramatic.
          </p>
        </div>
      )}
    </section>
  );
}
