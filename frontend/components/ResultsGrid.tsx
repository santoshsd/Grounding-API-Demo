import type { Run } from "@/lib/api";
import { ProviderCard } from "./ProviderCard";

export function ResultsGrid({ run }: { run: Run }) {
  const byProvider = new Map<string, typeof run.calls>();
  for (const c of run.calls) {
    const list = byProvider.get(c.provider) ?? [];
    list.push(c);
    byProvider.set(c.provider, list);
  }

  const serverLine = [
    run.fan_out_ms != null && run.fan_out_ms !== undefined
      ? `Providers (parallel): ${(run.fan_out_ms / 1000).toFixed(2)}s`
      : null,
    run.judge_ms != null && run.judge_ms !== undefined
      ? `Judge (all cards): ${(run.judge_ms / 1000).toFixed(2)}s`
      : null,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="flex flex-col gap-3">
      {serverLine ? (
        <p
          className="text-xs font-mono text-[var(--muted)] border border-[var(--border)] rounded-md px-3 py-2 bg-[var(--panel)]"
          title="Server-side phases for this run. Provider calls run in parallel; wall time is roughly max(latency) per card, not the sum."
        >
          {serverLine}
        </p>
      ) : null}
    <div className="grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(340px,1fr))]">
      {[...byProvider.entries()].map(([provider, calls]) => (
        <div key={provider} className="flex flex-col gap-3">
          {calls
            .sort((a, b) => Number(b.grounded) - Number(a.grounded))
            .map((c) => (
              <ProviderCard key={c.id} call={c} />
            ))}
        </div>
      ))}
    </div>
    </div>
  );
}
