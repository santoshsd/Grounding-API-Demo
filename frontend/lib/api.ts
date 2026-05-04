export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type Citation = { url: string; title?: string | null; snippet?: string | null };

export type TimingStage = { stage: string; ms: number };

export type JudgeScore = {
  correctness: number;
  groundedness: number;
  citation_support: number;
  rationale: string;
  judge_provider: string | null;
  judge_model: string | null;
  /** Total wall time for this judge call (ms). */
  latency_ms?: number | null;
  timings?: TimingStage[];
};

export type ProviderCall = {
  id: number;
  provider: string;
  grounded: boolean;
  model: string;
  answer: string;
  citations: Citation[];
  latency_ms: number;
  /** Wall time per downstream segment (search vs synthesis, single LLM call, etc.). */
  timings?: TimingStage[];
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number | null;
  error: string | null;
  judge: JudgeScore | null;
};

export type Run = {
  id: number;
  query: string;
  created_at: string;
  calls: ProviderCall[];
  /** Server-side parallel provider fan-out (POST /api/query), ms. */
  fan_out_ms?: number | null;
  /** Server-side LLM-as-judge phase (all providers), ms. */
  judge_ms?: number | null;
};

export type JudgeOption = {
  id: "google" | "anthropic";
  label: string;
  model: string;
  available: boolean;
};

export type JudgeConfig = {
  default: "google" | "anthropic";
  options: JudgeOption[];
};

export async function getJudgeConfig(): Promise<JudgeConfig> {
  const r = await fetch(`${API_BASE}/api/judge-config`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function runQuery(body: {
  query: string;
  providers: string[];
  include_ungrounded: boolean;
  run_judge: boolean;
  judge_provider?: "google" | "anthropic";
}): Promise<Run> {
  const r = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function listProviders(): Promise<string[]> {
  const r = await fetch(`${API_BASE}/api/providers`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function listRuns(): Promise<Run[]> {
  const r = await fetch(`${API_BASE}/api/runs`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getRun(id: number): Promise<Run> {
  const r = await fetch(`${API_BASE}/api/runs/${id}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
