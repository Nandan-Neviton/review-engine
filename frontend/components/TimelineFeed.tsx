/**
 * Activity timeline feed — vertical chronological event list.
 */

import { GitCommit, ShieldAlert, AlertTriangle, CheckCircle } from 'lucide-react';

export interface TimelineEvent {
  timestamp: string;
  author: string;
  repository: string;
  event: string;
  type: string;
}

interface TimelineFeedProps {
  events: TimelineEvent[];
}

const TYPE_CONFIG: Record<string, { icon: React.ReactNode; dot: string }> = {
  HIGH_RISK: {
    icon: <ShieldAlert className="w-3.5 h-3.5" />,
    dot: 'bg-red-500',
  },
  SENSITIVE: {
    icon: <AlertTriangle className="w-3.5 h-3.5" />,
    dot: 'bg-amber-500',
  },
  REVIEW: {
    icon: <GitCommit className="w-3.5 h-3.5" />,
    dot: 'bg-indigo-500',
  },
};

function formatTime(ts: string): string {
  try {
    return new Date(ts).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return ts;
  }
}

export function TimelineFeed({ events }: TimelineFeedProps) {
  if (events.length === 0) {
    return (
      <p className="text-slate-400 text-sm text-center py-10">
        No activity yet. Push code to generate timeline events.
      </p>
    );
  }

  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-3.5 top-0 bottom-0 w-px bg-slate-100" />

      <div className="space-y-4">
        {events.map((ev, i) => {
          const cfg = TYPE_CONFIG[ev.type] ?? TYPE_CONFIG['REVIEW'];
          return (
            <div key={i} className="flex gap-4 relative">
              {/* Dot */}
              <div className={`w-7 h-7 rounded-full ${cfg.dot} flex items-center justify-center text-white shrink-0 z-10`}>
                {cfg.icon}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 pb-1">
                <p className="text-sm text-slate-800 font-medium">{ev.event}</p>
                <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-0.5 text-xs text-slate-400">
                  <span>{ev.author}</span>
                  <span>·</span>
                  <span className="truncate max-w-xs">{ev.repository}</span>
                  <span>·</span>
                  <span>{formatTime(ev.timestamp)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
