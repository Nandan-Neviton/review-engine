/**
 * Repository Context Status card — shows governance context coverage
 * across repositories using data from /analytics/context-status.
 */

import { BookOpen, CheckCircle, XCircle, BookMarked, Tag } from 'lucide-react';

export interface ContextStatus {
  repositories_with_context: number;
  repositories_missing_context: number;
  loaded_user_stories: number;
  latest_detected_story: string | null;
  repos_with_context: string[];
  repos_missing_context: string[];
}

interface ContextStatusCardProps {
  status: ContextStatus;
}

export function ContextStatusCard({ status }: ContextStatusCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 space-y-5">

      {/* Top metric row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">

        <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-center">
          <BookOpen className="w-5 h-5 text-indigo-500 mx-auto mb-1" />
          <p className="text-2xl font-bold text-indigo-800">{status.repositories_with_context}</p>
          <p className="text-xs text-indigo-600 font-medium mt-0.5">Context Available</p>
        </div>

        <div className={`rounded-xl p-4 text-center border ${
          status.repositories_missing_context > 0
            ? 'bg-amber-50 border-amber-100'
            : 'bg-slate-50 border-slate-100'
        }`}>
          <XCircle className={`w-5 h-5 mx-auto mb-1 ${
            status.repositories_missing_context > 0 ? 'text-amber-400' : 'text-slate-300'
          }`} />
          <p className={`text-2xl font-bold ${
            status.repositories_missing_context > 0 ? 'text-amber-800' : 'text-slate-400'
          }`}>{status.repositories_missing_context}</p>
          <p className={`text-xs font-medium mt-0.5 ${
            status.repositories_missing_context > 0 ? 'text-amber-600' : 'text-slate-400'
          }`}>Missing Context</p>
        </div>

        <div className="bg-violet-50 border border-violet-100 rounded-xl p-4 text-center">
          <BookMarked className="w-5 h-5 text-violet-500 mx-auto mb-1" />
          <p className="text-2xl font-bold text-violet-800">{status.loaded_user_stories}</p>
          <p className="text-xs text-violet-600 font-medium mt-0.5">User Stories</p>
        </div>

        <div className={`rounded-xl p-4 text-center border ${
          status.latest_detected_story
            ? 'bg-emerald-50 border-emerald-100'
            : 'bg-slate-50 border-slate-100'
        }`}>
          <Tag className={`w-5 h-5 mx-auto mb-1 ${
            status.latest_detected_story ? 'text-emerald-500' : 'text-slate-300'
          }`} />
          <p className={`text-sm font-bold font-mono mt-0.5 ${
            status.latest_detected_story ? 'text-emerald-800' : 'text-slate-400'
          }`}>
            {status.latest_detected_story ?? '—'}
          </p>
          <p className={`text-xs font-medium mt-0.5 ${
            status.latest_detected_story ? 'text-emerald-600' : 'text-slate-400'
          }`}>Last Detected Story</p>
        </div>

      </div>

      {/* Repos with context */}
      {status.repos_with_context.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Repositories with Context
          </p>
          <div className="flex flex-wrap gap-2">
            {status.repos_with_context.map((repo) => (
              <span
                key={repo}
                className="inline-flex items-center gap-1 text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full px-2.5 py-0.5 font-medium"
              >
                <CheckCircle className="w-3 h-3" />
                {repo}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Repos missing context */}
      {status.repos_missing_context.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Repositories Missing Context
          </p>
          <div className="flex flex-wrap gap-2">
            {status.repos_missing_context.map((repo) => (
              <span
                key={repo}
                className="inline-flex items-center gap-1 text-xs bg-amber-50 text-amber-700 border border-amber-200 rounded-full px-2.5 py-0.5 font-medium"
              >
                <XCircle className="w-3 h-3" />
                {repo}
              </span>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
