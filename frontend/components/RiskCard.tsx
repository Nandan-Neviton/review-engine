/**
 * Risk distribution card — shows count for a single risk level.
 */

interface RiskCardProps {
  level: 'LOW' | 'MEDIUM' | 'HIGH';
  count: number;
  total: number;
}

const CONFIG = {
  LOW: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    badgeBg: 'bg-emerald-100',
    badgeText: 'text-emerald-700',
    countText: 'text-emerald-800',
    bar: 'bg-emerald-400',
    label: 'Low Risk',
    description: 'Safe to merge',
  },
  MEDIUM: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-700',
    countText: 'text-amber-800',
    bar: 'bg-amber-400',
    label: 'Medium Risk',
    description: 'Review recommended',
  },
  HIGH: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    badgeBg: 'bg-red-100',
    badgeText: 'text-red-700',
    countText: 'text-red-800',
    bar: 'bg-red-400',
    label: 'High Risk',
    description: 'Immediate review required',
  },
};

export function RiskCard({ level, count, total }: RiskCardProps) {
  const c = CONFIG[level];
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;

  return (
    <div className={`${c.bg} ${c.border} border rounded-2xl p-6`}>
      <div className="flex items-center justify-between mb-3">
        <span className={`${c.badgeBg} ${c.badgeText} text-xs font-bold px-2.5 py-1 rounded-full`}>
          {level}
        </span>
        <span className="text-xs text-slate-400 font-medium">{pct}%</span>
      </div>
      <p className={`text-4xl font-bold ${c.countText} leading-none`}>{count}</p>
      <p className="text-sm text-slate-600 mt-1 font-medium">{c.label} Reviews</p>
      <p className="text-xs text-slate-400 mt-0.5">{c.description}</p>

      {/* Mini progress bar */}
      <div className="mt-4 h-1.5 bg-white/60 rounded-full overflow-hidden">
        <div
          className={`${c.bar} h-full rounded-full transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
