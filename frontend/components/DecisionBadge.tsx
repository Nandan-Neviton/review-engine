/**
 * Decision badge — APPROVED | NEEDS_REVIEW | BLOCKED
 */

const STYLES: Record<string, string> = {
  APPROVED:     'bg-emerald-100 text-emerald-700 ring-emerald-200',
  NEEDS_REVIEW: 'bg-amber-100   text-amber-700   ring-amber-200',
  BLOCKED:      'bg-red-100     text-red-700     ring-red-200',
};

const ICONS: Record<string, string> = {
  APPROVED:     '✓',
  NEEDS_REVIEW: '◎',
  BLOCKED:      '✕',
};

interface DecisionBadgeProps {
  decision: string;
  size?: 'sm' | 'md';
}

export function DecisionBadge({ decision, size = 'sm' }: DecisionBadgeProps) {
  const cls = STYLES[decision] ?? 'bg-slate-100 text-slate-600 ring-slate-200';
  const padding = size === 'md' ? 'px-3 py-1 text-sm gap-1.5' : 'px-2 py-0.5 text-xs gap-1';
  return (
    <span className={`inline-flex items-center font-semibold rounded-full ring-1 ${cls} ${padding}`}>
      <span>{ICONS[decision] ?? '?'}</span>
      {decision}
    </span>
  );
}
