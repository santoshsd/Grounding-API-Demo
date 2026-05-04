import type { ProviderCall } from "@/lib/api";

function formatStages(call: ProviderCall): string | null {
  const t = call.timings;
  if (!t?.length) return null;
  return t.map((s) => `${s.stage} ${(s.ms / 1000).toFixed(2)}s`).join(" · ");
}

export function MetricsBar({ call }: { call: ProviderCall }) {
  const cost = call.cost_usd != null ? `$${call.cost_usd.toFixed(4)}` : "—";
  const tokens =
    call.input_tokens != null && call.output_tokens != null
      ? `${call.input_tokens}→${call.output_tokens}`
      : "—";
  const stages = formatStages(call);
  return (
    <div className="flex flex-col gap-0.5 text-xs text-[var(--muted)]">
      <div className="flex gap-4 flex-wrap">
        <span title={stages ?? "Total wall time for this provider call"}>
          {(call.latency_ms / 1000).toFixed(2)}s total
        </span>
        <span>{tokens} tok</span>
        <span>{cost}</span>
      </div>
      {stages ? (
        <span className="font-mono text-[10px] opacity-90" title="Per downstream segment">
          {stages}
        </span>
      ) : null}
    </div>
  );
}
