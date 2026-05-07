/**
 * Overview metric card — icon, large number, title, description.
 */

interface MetricCardProps {
  title: string;
  value: number | string;
  description: string;
  icon: React.ReactNode;
  /** Tailwind classes for the icon wrapper background */
  iconBg: string;
  /** Tailwind classes for the icon color */
  iconColor: string;
}

export function MetricCard({ title, value, description, icon, iconBg, iconColor }: MetricCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 flex items-start gap-4 hover:shadow-md transition-shadow">
      <div className={`${iconBg} p-3 rounded-xl shrink-0`}>
        <div className={`${iconColor} w-6 h-6`}>{icon}</div>
      </div>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
        <p className="text-3xl font-bold text-slate-900 mt-1 leading-none">{value}</p>
        <p className="text-xs text-slate-400 mt-1.5">{description}</p>
      </div>
    </div>
  );
}
