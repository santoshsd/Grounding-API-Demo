"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Label,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const TOOLTIP_STYLE = {
  background: "#1b2028",
  border: "1px solid #3a4553",
  borderRadius: 6,
  color: "#e6edf3",
  fontSize: 12,
  padding: "8px 10px",
};
const TOOLTIP_LABEL_STYLE = { color: "#e6edf3", fontWeight: 600, marginBottom: 4 };
const TOOLTIP_ITEM_STYLE = { color: "#e6edf3" };

const PALETTE = [
  "#7aa2f7", "#9ece6a", "#e0af68", "#bb9af7", "#f7768e", "#7dcfff", "#ff9e64",
];

function ScatterTooltip({ active, payload }: { active?: boolean; payload?: { payload: ScatterPoint }[] }) {
  if (!active || !payload || !payload.length) return null;
  const p = payload[0].payload;
  return (
    <div style={TOOLTIP_STYLE}>
      <div style={TOOLTIP_LABEL_STYLE}>{p.name}</div>
      <div>Latency: <span style={{ color: "#7aa2f7" }}>{p.x.toFixed(2)} s</span></div>
      <div>Avg judge score: <span style={{ color: "#9ece6a" }}>{p.y.toFixed(2)} / 5</span></div>
      <div style={{ color: "#8b96a3", marginTop: 4 }}>Based on {p.count} call{p.count === 1 ? "" : "s"}</div>
    </div>
  );
}

type ScatterPoint = { name: string; x: number; y: number; count: number; grounded: boolean };
import { listRuns, type Run } from "@/lib/api";

type Agg = {
  provider: string;
  grounded: boolean;
  correctness: number;
  groundedness: number;
  citation_support: number;
  avg_latency: number;
  count: number;
};

function aggregate(runs: Run[]): Agg[] {
  const key = (p: string, g: boolean) => `${p}|${g}`;
  const acc = new Map<string, Agg & { _sum: { c: number; g: number; s: number; l: number } }>();
  for (const r of runs) {
    for (const c of r.calls) {
      if (!c.judge) continue;
      const k = key(c.provider, c.grounded);
      const cur = acc.get(k) ?? {
        provider: c.provider,
        grounded: c.grounded,
        correctness: 0,
        groundedness: 0,
        citation_support: 0,
        avg_latency: 0,
        count: 0,
        _sum: { c: 0, g: 0, s: 0, l: 0 },
      };
      cur._sum.c += c.judge.correctness;
      cur._sum.g += c.judge.groundedness;
      cur._sum.s += c.judge.citation_support;
      cur._sum.l += c.latency_ms;
      cur.count += 1;
      acc.set(k, cur);
    }
  }
  return [...acc.values()].map((a) => ({
    provider: a.provider,
    grounded: a.grounded,
    correctness: a._sum.c / a.count,
    groundedness: a._sum.g / a.count,
    citation_support: a._sum.s / a.count,
    avg_latency: a._sum.l / a.count,
    count: a.count,
  }));
}

export default function ComparePage() {
  const [runs, setRuns] = useState<Run[]>([]);
  useEffect(() => {
    listRuns().then(setRuns).catch(() => setRuns([]));
  }, []);

  const agg = aggregate(runs);
  const barData = agg.map((a) => ({
    name: `${a.provider}${a.grounded ? "" : " (base)"}`,
    correctness: +a.correctness.toFixed(2),
    groundedness: +a.groundedness.toFixed(2),
    citation_support: +a.citation_support.toFixed(2),
  }));
  const scatterData: ScatterPoint[] = agg.map((a) => ({
    name: `${a.provider}${a.grounded ? "" : " (baseline)"}`,
    x: +(a.avg_latency / 1000).toFixed(2),
    y: +((a.correctness + a.groundedness + a.citation_support) / 3).toFixed(2),
    count: a.count,
    grounded: a.grounded,
  }));
  const groundedPoints = scatterData.filter((p) => p.grounded);
  const baselinePoints = scatterData.filter((p) => !p.grounded);

  return (
    <div className="flex flex-col gap-8">
      <section>
        <h2 className="text-sm text-[var(--muted)] mb-3">
          Average judge scores by provider ({runs.length} runs)
        </h2>
        <div className="h-80 bg-[var(--panel)] border border-[var(--border)] rounded-lg p-3">
          <ResponsiveContainer>
            <BarChart data={barData}>
              <CartesianGrid stroke="#232a33" strokeDasharray="3 3" />
              <XAxis dataKey="name" stroke="#8b96a3" fontSize={11} />
              <YAxis stroke="#8b96a3" domain={[0, 5]} fontSize={11} />
              <Tooltip
                cursor={{ fill: "rgba(122,162,247,0.08)" }}
                contentStyle={TOOLTIP_STYLE}
                labelStyle={TOOLTIP_LABEL_STYLE}
                itemStyle={TOOLTIP_ITEM_STYLE}
              />
              <Legend wrapperStyle={{ color: "#e6edf3", fontSize: 12 }} />
              <Bar dataKey="correctness" name="Correctness" fill="#7aa2f7" />
              <Bar dataKey="groundedness" name="Groundedness" fill="#9ece6a" />
              <Bar dataKey="citation_support" name="Citation support" fill="#e0af68" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section>
        <h2 className="text-sm text-[var(--muted)] mb-1">Latency vs. avg judge score</h2>
        <p className="text-xs text-[var(--muted)] mb-3">
          Each point is one provider configuration. Lower-left = slow and low quality; upper-left = fast and high quality (the sweet spot).
        </p>
        <div className="h-96 bg-[var(--panel)] border border-[var(--border)] rounded-lg p-3 pb-6">
          <ResponsiveContainer>
            <ScatterChart margin={{ top: 10, right: 30, bottom: 40, left: 30 }}>
              <CartesianGrid stroke="#232a33" strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="x"
                name="Latency"
                stroke="#8b96a3"
                fontSize={11}
                tickFormatter={(v) => `${v}s`}
              >
                <Label
                  value="Average latency (seconds, lower is better)"
                  position="insideBottom"
                  offset={-20}
                  fill="#e6edf3"
                  fontSize={12}
                />
              </XAxis>
              <YAxis
                type="number"
                dataKey="y"
                name="Avg score"
                domain={[0, 5]}
                stroke="#8b96a3"
                fontSize={11}
              >
                <Label
                  value="Avg judge score (1–5, higher is better)"
                  angle={-90}
                  position="insideLeft"
                  offset={-15}
                  style={{ textAnchor: "middle" }}
                  fill="#e6edf3"
                  fontSize={12}
                />
              </YAxis>
              <Tooltip cursor={{ strokeDasharray: "3 3", stroke: "#7aa2f7" }} content={<ScatterTooltip />} />
              <Legend verticalAlign="top" height={28} wrapperStyle={{ color: "#e6edf3", fontSize: 12 }} />
              <Scatter name="Grounded" data={groundedPoints} fill="#7aa2f7" shape="circle">
                {groundedPoints.map((p, i) => (
                  <Cell key={p.name} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Scatter>
              <Scatter name="Baseline (ungrounded)" data={baselinePoints} fill="#f7768e" shape="triangle" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
