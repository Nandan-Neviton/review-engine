/**
 * Engineering Health Score card — prominent score gauge with label.
 */

interface HealthScoreProps {
  score: number;
  label: string;
}

const LABEL_CONFIG: Record<string, { ring: string; text: string; bg: string; desc: string }> = {
  EXCELLENT: { ring: 'stroke-emerald-500', text: 'text-emerald-600', bg: 'bg-emerald-50', desc: 'Engineering practices are healthy' },
  GOOD:      { ring: 'stroke-indigo-500',  text: 'text-indigo-600',  bg: 'bg-indigo-50',  desc: 'Minor improvements recommended' },
  WARNING:   { ring: 'stroke-amber-500',   text: 'text-amber-600',   bg: 'bg-amber-50',   desc: 'Governance attention needed' },
  CRITICAL:  { ring: 'stroke-red-500',     text: 'text-red-600',     bg: 'bg-red-50',     desc: 'Immediate intervention required' },
};

export function HealthScoreCard({ score, label }: HealthScoreProps) {
  const cfg = LABEL_CONFIG[label] ?? LABEL_CONFIG['GOOD'];

  // SVG ring parameters
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className={`${cfg.bg} rounded-2xl border border-slate-100 shadow-sm p-6 flex items-center gap-6`}>
      {/* Ring gauge */}
      <div className="shrink-0 relative w-24 h-24">
        <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
          {/* Track */}
          <circle
            cx="50" cy="50" r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-slate-200"
          />
          {/* Progress */}
          <circle
            cx="50" cy="50" r={radius}
            fill="none"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={`${cfg.ring} transition-all duration-700`}
          />
        </svg>
        <span className={`absolute inset-0 flex items-center justify-center text-2xl font-bold ${cfg.text}`}>
          {score}
        </span>
      </div>

      <div>
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Engineering Health</p>
        <p className={`text-2xl font-bold mt-1 ${cfg.text}`}>{label}</p>
        <p className="text-xs text-slate-500 mt-1">{cfg.desc}</p>
        <p className="text-xs text-slate-400 mt-0.5">Score: {score} / 100</p>
      </div>
    </div>
  );
}
