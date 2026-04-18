import type { ProviderCall } from "@/lib/api";
import { CitationList } from "./CitationList";
import { JudgeScoreBadge } from "./JudgeScore";
import { MetricsBar } from "./MetricsBar";

export function ProviderCard({ call }: { call: ProviderCall }) {
  return (
    <div className="border border-[var(--border)] bg-[var(--panel)] rounded-lg p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-semibold">{call.provider}</span>
          <span
            className={`text-xs px-2 py-0.5 rounded ${
              call.grounded
                ? "bg-[var(--accent)] text-[var(--bg)]"
                : "border border-[var(--border)] text-[var(--muted)]"
            }`}
          >
            {call.grounded ? "grounded" : "baseline"}
          </span>
        </div>
        <span className="text-xs text-[var(--muted)] font-mono" title="Model used to generate this answer">answer: {call.model}</span>
      </div>
      <MetricsBar call={call} />
      {call.error ? (
        <p className="text-[var(--bad)] text-sm font-mono">⚠ {call.error}</p>
      ) : (
        <p className="text-sm whitespace-pre-wrap leading-relaxed">{call.answer}</p>
      )}
      <div className="border-t border-[var(--border)] pt-3">
        <CitationList citations={call.citations} />
      </div>
      <div className="border-t border-[var(--border)] pt-3">
        <JudgeScoreBadge score={call.judge} />
      </div>
    </div>
  );
}
