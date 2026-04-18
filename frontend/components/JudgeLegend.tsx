import { JUDGE_DIMENSIONS } from "./JudgeScore";

export function JudgeLegend() {
  return (
    <div className="border border-[var(--border)] bg-[var(--panel)] rounded-lg p-3 text-xs">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <span className="text-[var(--muted)] font-semibold">Judge scores:</span>
        {JUDGE_DIMENSIONS.map((d) => (
          <span
            key={d.code}
            title={d.tooltip}
            className="flex items-center gap-1 cursor-help"
          >
            <span
              className="px-1.5 py-0.5 rounded font-mono"
              style={{ backgroundColor: "var(--muted)", color: "#0b0d10" }}
            >
              {d.code}N
            </span>
            <span>{d.name}</span>
          </span>
        ))}
        <span className="text-[var(--muted)] ml-auto">
          N = 1 (poor) to 5 (excellent) · green ≥ 4 · red ≤ 2 · hover any pill for details
        </span>
      </div>
    </div>
  );
}
