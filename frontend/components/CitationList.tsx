import type { Citation } from "@/lib/api";

function domain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

export function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations.length) {
    return <p className="text-xs text-[var(--muted)] italic">No citations</p>;
  }
  return (
    <ol className="space-y-1 text-xs">
      {citations.map((c, i) => (
        <li key={i} className="flex gap-2">
          <span className="text-[var(--muted)]">[{i + 1}]</span>
          <a
            href={c.url}
            target="_blank"
            rel="noreferrer"
            className="text-[var(--accent)] hover:underline truncate"
            title={c.title || c.url}
          >
            {c.title || domain(c.url)}
          </a>
          <span className="text-[var(--muted)] shrink-0">{domain(c.url)}</span>
        </li>
      ))}
    </ol>
  );
}
