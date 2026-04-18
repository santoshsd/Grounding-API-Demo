import type { Run } from "@/lib/api";
import { ProviderCard } from "./ProviderCard";

export function ResultsGrid({ run }: { run: Run }) {
  const byProvider = new Map<string, typeof run.calls>();
  for (const c of run.calls) {
    const list = byProvider.get(c.provider) ?? [];
    list.push(c);
    byProvider.set(c.provider, list);
  }

  return (
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
  );
}
