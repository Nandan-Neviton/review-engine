/**
 * Reusable risk/severity badge.
 * LOW → green | MEDIUM → yellow | HIGH → red
 */

const STYLES: Record<string, string> = {
  LOW: 'bg-emerald-100 text-emerald-700 ring-emerald-200',
  MEDIUM: 'bg-amber-100 text-amber-700 ring-amber-200',
  HIGH: 'bg-red-100 text-red-700 ring-red-200',
};

interface RiskBadgeProps {
  level: string;
  size?: 'sm' | 'md';
}

export function RiskBadge({ level, size = 'sm' }: RiskBadgeProps) {
  const cls = STYLES[level] ?? 'bg-gray-100 text-gray-600 ring-gray-200';
  const padding = size === 'md' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs';
  return (
    <span className={`inline-flex items-center font-semibold rounded-full ring-1 ${cls} ${padding}`}>
      {level}
    </span>
  );
}
