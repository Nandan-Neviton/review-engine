/**
 * Hotspot analytics table — most-modified files ranked by modification count.
 */

interface Hotspot {
  filename: string;
  modifications: number;
  risk_score: number;
}

interface HotspotTableProps {
  hotspots: Hotspot[];
}

export function HotspotTable({ hotspots }: HotspotTableProps) {
  const top = hotspots.slice(0, 10);
  const maxMods = top[0]?.modifications ?? 1;

  if (top.length === 0) {
    return (
      <p className="text-slate-400 text-sm text-center py-10">
        No file hotspot data yet.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {top.map((h, i) => {
        const pct = Math.round((h.modifications / maxMods) * 100);
        const isHot = i < 3;
        return (
          <div key={i} className="flex items-center gap-3">
            <span className={`w-5 text-xs font-bold shrink-0 ${isHot ? 'text-red-500' : 'text-slate-400'}`}>
              {i + 1}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-0.5">
                <span className="font-mono text-xs text-slate-700 truncate max-w-xs">
                  {h.filename}
                </span>
                <div className="flex items-center gap-3 shrink-0 ml-2 text-xs text-slate-500">
                  <span>{h.modifications} mod{h.modifications !== 1 ? 's' : ''}</span>
                  <span className="text-slate-300">|</span>
                  <span>risk Σ {h.risk_score}</span>
                </div>
              </div>
              <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${isHot ? 'bg-red-400' : 'bg-indigo-300'}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
