'use client';

/**
 * Collapsible review card — shows summary + expandable findings and file diffs.
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, GitCommit, GitBranch, User, Clock, FileCode } from 'lucide-react';
import { RiskBadge } from './RiskBadge';
import { DecisionBadge } from './DecisionBadge';

export interface Finding {
  category: string;
  severity: string;
  message: string;
  file: string;
}

export interface FileChanged {
  filename: string;
  status: string;
  additions: number;
  deletions: number;
  changes: number;
  patch: string | null;
}

export interface Review {
  status: string;
  repository: string;
  branch: string;
  commit_sha: string;
  author: string;
  timestamp: string;
  risk_score: string;
  risk_score_value: number;
  review_decision?: string;
  total_files_changed: number;
  findings: Finding[];
  files_changed: FileChanged[];
}

interface ReviewCardProps {
  review: Review;
}

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

export function ReviewCard({ review }: ReviewCardProps) {
  const [expanded, setExpanded] = useState(false);
  const hasFindingsOrFiles =
    (review.findings?.length ?? 0) > 0 || (review.files_changed?.length ?? 0) > 0;

  return (
    <div className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
      {/* Summary row */}
      <div
        className={`p-5 ${hasFindingsOrFiles ? 'cursor-pointer hover:bg-slate-50' : ''} transition-colors`}
        onClick={() => hasFindingsOrFiles && setExpanded((v) => !v)}
      >
        <div className="flex items-start justify-between gap-4">
          {/* Left: repo + risk */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-semibold text-slate-900 truncate text-sm">
                {review.repository}
              </span>
              <RiskBadge level={review.risk_score} size="sm" />
              {review.review_decision && (
                <DecisionBadge decision={review.review_decision} size="sm" />
              )}
            </div>

            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <GitCommit className="w-3 h-3" />
                <span className="font-mono">{review.commit_sha?.slice(0, 8) ?? '—'}</span>
              </span>
              <span className="flex items-center gap-1">
                <GitBranch className="w-3 h-3" />
                {review.branch}
              </span>
              <span className="flex items-center gap-1">
                <User className="w-3 h-3" />
                {review.author}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatTime(review.timestamp)}
              </span>
              <span className="flex items-center gap-1">
                <FileCode className="w-3 h-3" />
                {review.total_files_changed} file{review.total_files_changed !== 1 ? 's' : ''}
              </span>
            </div>
          </div>

          {/* Right: expand toggle */}
          {hasFindingsOrFiles && (
            <div className="shrink-0 text-slate-400 mt-0.5">
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </div>
          )}
        </div>

        {/* Findings summary chips */}
        {(review.findings?.length ?? 0) > 0 && !expanded && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {review.findings.slice(0, 3).map((f, i) => (
              <span
                key={i}
                className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full truncate max-w-xs"
              >
                {f.message}
              </span>
            ))}
            {review.findings.length > 3 && (
              <span className="text-xs text-slate-400 px-2 py-0.5">
                +{review.findings.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-slate-100 bg-slate-50/50 p-5 space-y-5">
          {/* Findings list */}
          {(review.findings?.length ?? 0) > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Findings ({review.findings.length})
              </h4>
              <div className="space-y-1.5">
                {review.findings.map((f, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 bg-white border border-slate-100 rounded-xl px-3 py-2 text-xs"
                  >
                    <RiskBadge level={f.severity} />
                    <div className="flex-1 min-w-0">
                      <span className="text-slate-600">{f.message}</span>
                      <span className="text-slate-400 font-mono ml-2 truncate block">
                        {f.file}
                      </span>
                    </div>
                    <span className="shrink-0 text-slate-300 text-xs bg-slate-100 px-1.5 py-0.5 rounded font-mono">
                      {f.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Changed files */}
          {(review.files_changed?.length ?? 0) > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Changed Files ({review.files_changed.length})
              </h4>
              <div className="space-y-3">
                {review.files_changed.map((file, i) => (
                  <div
                    key={i}
                    className="bg-white border border-slate-100 rounded-xl overflow-hidden"
                  >
                    {/* File header */}
                    <div className="flex items-center justify-between px-4 py-2.5 bg-slate-100/80 border-b border-slate-100">
                      <span className="font-mono text-xs text-slate-700 truncate flex-1 mr-2">
                        {file.filename}
                      </span>
                      <div className="flex items-center gap-2 text-xs shrink-0">
                        <span className="text-slate-400 bg-slate-200/60 px-1.5 py-0.5 rounded text-xs">
                          {file.status}
                        </span>
                        <span className="text-emerald-600 font-semibold">+{file.additions}</span>
                        <span className="text-red-500 font-semibold">−{file.deletions}</span>
                      </div>
                    </div>

                    {/* Diff patch */}
                    {file.patch ? (
                      <pre className="bg-[#0d1117] text-emerald-400 p-4 text-xs leading-5 overflow-x-auto max-h-72 overflow-y-auto font-mono whitespace-pre scrollbar-thin">
                        {file.patch}
                      </pre>
                    ) : (
                      <p className="text-xs text-slate-400 px-4 py-3 italic">No patch available</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
