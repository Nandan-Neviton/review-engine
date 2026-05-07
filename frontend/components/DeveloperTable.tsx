/**
 * Developer analytics table — per-author push, files, and risk metrics.
 */

import { RiskBadge } from './RiskBadge';

export interface Developer {
  author: string;
  total_pushes: number;
  avg_files_changed: number;
  avg_risk_score: number;
}

interface DeveloperTableProps {
  developers: Developer[];
}

function riskLabel(score: number): string {
  if (score >= 6) return 'HIGH';
  if (score >= 3) return 'MEDIUM';
  return 'LOW';
}

export function DeveloperTable({ developers }: DeveloperTableProps) {
  if (developers.length === 0) {
    return (
      <p className="text-slate-400 text-sm text-center py-10">
        No developer data yet — push code to populate metrics.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100">
            {['Developer', 'Total Pushes', 'Avg Files Changed', 'Avg Risk Score'].map((h) => (
              <th
                key={h}
                className="pb-3 pt-1 text-left font-semibold text-slate-400 text-xs uppercase tracking-wider first:pl-0 last:pr-0 px-4"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {developers.map((dev, i) => (
            <tr
              key={i}
              className="hover:bg-slate-50 transition-colors group"
            >
              <td className="py-3.5 pl-0 pr-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                    {dev.author.charAt(0).toUpperCase()}
                  </div>
                  <span className="font-medium text-slate-800">{dev.author}</span>
                </div>
              </td>
              <td className="py-3.5 px-4 text-slate-600 font-medium">{dev.total_pushes}</td>
              <td className="py-3.5 px-4 text-slate-600">{dev.avg_files_changed}</td>
              <td className="py-3.5 px-4">
                <div className="flex items-center gap-2">
                  <span className="text-slate-600 font-mono text-xs">{dev.avg_risk_score}</span>
                  <RiskBadge level={riskLabel(dev.avg_risk_score)} />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
