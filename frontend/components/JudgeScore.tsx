import type { JudgeScore as Score } from "@/lib/api";

function color(n: number) {
  if (n >= 4) return "var(--good)";
  if (n <= 2) return "var(--bad)";
  return "var(--muted)";
}

export const JUDGE_DIMENSIONS = [
  {
    code: "Cor",
    name: "Correctness",
    tooltip:
      "Is the factual content accurate? Penalizes hallucinations. Scale 1 (poor) to 5 (excellent).",
  },
  {
    code: "Grd",
    name: "Groundedness",
    tooltip:
      "Does the answer appear anchored in the cited sources rather than invented or speculative? Scale 1–5.",
  },
  {
    code: "Cit",
    name: "Citation support",
    tooltip:
      "Do the citations actually support the claims? No citations scores 1 unless the answer admits ignorance. Scale 1–5.",
  },
] as const;

function Pill({ code, name, tooltip, n }: {
  code: string; name: string; tooltip: string; n: number;
}) {
  return (
    <span
      className="px-2 py-0.5 rounded text-xs font-mono cursor-help"
      style={{ backgroundColor: color(n), color: "#0b0d10" }}
      title={`${name} (${n}/5): ${tooltip}`}
    >
      {code}
      {n}
    </span>
  );
}

function judgeTimingLine(score: Score): string | null {
  const parts: string[] = [];
  if (score.latency_ms != null) {
    parts.push(`${(score.latency_ms / 1000).toFixed(2)}s judge total`);
  }
  if (score.timings?.length) {
    parts.push(
      score.timings.map((s) => `${s.stage} ${(s.ms / 1000).toFixed(2)}s`).join(" · ")
    );
  }
  return parts.length ? parts.join(" — ") : null;
}

export function JudgeScoreBadge({ score }: { score: Score | null }) {
  if (!score) {
    return <span className="text-xs text-[var(--muted)]">Not judged</span>;
  }
  const values = [score.correctness, score.groundedness, score.citation_support];
  const timing = judgeTimingLine(score);
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2 flex-wrap">
        {JUDGE_DIMENSIONS.map((d, i) => (
          <Pill key={d.code} {...d} n={values[i]} />
        ))}
        {score.judge_provider && (
          <span
            className="text-[10px] text-[var(--muted)] border border-[var(--border)] rounded px-1.5 py-0.5"
            title={`This response was scored by ${score.judge_provider} (${score.judge_model ?? ""})`}
          >
            judged by {score.judge_provider}
            {score.judge_model ? ` · ${score.judge_model}` : ""}
          </span>
        )}
      </div>
      {timing ? (
        <p className="text-[10px] font-mono text-[var(--muted)]" title="LLM-as-judge latency breakdown">
          {timing}
        </p>
      ) : null}
      <p className="text-xs text-[var(--muted)] italic">{score.rationale}</p>
    </div>
  );
}
