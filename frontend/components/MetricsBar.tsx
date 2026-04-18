import type { ProviderCall } from "@/lib/api";

export function MetricsBar({ call }: { call: ProviderCall }) {
  const cost = call.cost_usd != null ? `$${call.cost_usd.toFixed(4)}` : "—";
  const tokens =
    call.input_tokens != null && call.output_tokens != null
      ? `${call.input_tokens}→${call.output_tokens}`
      : "—";
  return (
    <div className="flex gap-4 text-xs text-[var(--muted)]">
      <span>{(call.latency_ms / 1000).toFixed(2)}s</span>
      <span>{tokens} tok</span>
      <span>{cost}</span>
    </div>
  );
}
