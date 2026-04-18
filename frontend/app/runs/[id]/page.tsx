import { JudgeLegend } from "@/components/JudgeLegend";
import { ResultsGrid } from "@/components/ResultsGrid";
import { getRun } from "@/lib/api";

export default async function RunPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const run = await getRun(Number(id));
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-lg font-semibold">
        Run #{run.id} — {run.query}
      </h1>
      <p className="text-xs text-[var(--muted)]">{new Date(run.created_at).toLocaleString()}</p>
      <JudgeLegend />
      <ResultsGrid run={run} />
    </div>
  );
}
