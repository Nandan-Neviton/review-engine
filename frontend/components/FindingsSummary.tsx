/**
 * Findings distribution — category breakdown cards.
 */

const CATEGORY_CONFIG: Record<string, { bg: string; text: string; border: string; label: string }> = {
  SECURITY:         { bg: 'bg-red-50',     text: 'text-red-700',    border: 'border-red-200',    label: 'Security' },
  SENSITIVE_MODULE: { bg: 'bg-orange-50',  text: 'text-orange-700', border: 'border-orange-200', label: 'Sensitive Module' },
  GOVERNANCE:       { bg: 'bg-amber-50',   text: 'text-amber-700',  border: 'border-amber-200',  label: 'Governance' },
  CODE_QUALITY:     { bg: 'bg-blue-50',    text: 'text-blue-700',   border: 'border-blue-200',   label: 'Code Quality' },
  ARCHITECTURE:     { bg: 'bg-violet-50',  text: 'text-violet-700', border: 'border-violet-200', label: 'Architecture' },
};

const FALLBACK = { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200', label: 'Other' };

interface FindingsSummaryProps {
  summary: Record<string, number>;
}

export function FindingsSummary({ summary }: FindingsSummaryProps) {
  const entries = Object.entries(summary).sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) {
    return (
      <p className="text-slate-400 text-sm text-center py-10">
        No findings yet.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      {entries.map(([category, count]) => {
        const cfg = CATEGORY_CONFIG[category] ?? FALLBACK;
        return (
          <div
            key={category}
            className={`${cfg.bg} ${cfg.border} border rounded-2xl p-4 text-center`}
          >
            <p className={`text-3xl font-bold ${cfg.text} leading-none`}>{count}</p>
            <p className={`text-xs font-semibold ${cfg.text} mt-1.5`}>{cfg.label}</p>
          </div>
        );
      })}
    </div>
  );
}
