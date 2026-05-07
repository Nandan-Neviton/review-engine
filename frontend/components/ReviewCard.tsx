'use client';

/**
 * Collapsible review card — shows summary + expandable findings and file diffs.
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, GitCommit, GitBranch, User, Clock, FileCode, BookOpen, ShieldCheck } from 'lucide-react';
import { RiskBadge } from './RiskBadge';
import { DecisionBadge } from './DecisionBadge';
import { AIReviewSection, AIReviewResult } from './AIReviewSection';

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
  // Context metadata
  repository_context_loaded?: boolean;
  loaded_context_files?: string[];
  detected_user_story?: string | null;
  available_user_stories?: string[];
  commit_message?: string;
  // AI governance review
  ai_review?: AIReviewResult;
  // Balanced decision engine outputs
  decision_reason?: string[];
  governance_confidence?: number;
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
              {review.governance_confidence !== undefined && (
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                    review.governance_confidence >= 80
                      ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                      : review.governance_confidence >= 50
                      ? 'text-amber-600 bg-amber-50 border-amber-200'
                      : 'text-red-600 bg-red-50 border-red-200'
                  }`}
                >
                  {review.governance_confidence}% confidence
                </span>
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

          {/* ── Governance Decision ── */}
          {((review.decision_reason?.length ?? 0) > 0 || review.governance_confidence !== undefined) && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <ShieldCheck className="w-3 h-3" />
                Governance Decision
              </h4>
              <div className="bg-white border border-slate-100 rounded-xl p-4 space-y-3">

                {/* Confidence bar */}
                {review.governance_confidence !== undefined && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-slate-500">Governance Confidence</span>
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded-full border ${
                          review.governance_confidence >= 80
                            ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                            : review.governance_confidence >= 50
                            ? 'text-amber-600 bg-amber-50 border-amber-200'
                            : 'text-red-600 bg-red-50 border-red-200'
                        }`}
                      >
                        {review.governance_confidence}%
                      </span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          review.governance_confidence >= 80
                            ? 'bg-emerald-500'
                            : review.governance_confidence >= 50
                            ? 'bg-amber-400'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(100, review.governance_confidence)}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Decision reasoning */}
                {(review.decision_reason?.length ?? 0) > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 mb-1.5">Reasoning</p>
                    <ul className="space-y-1">
                      {review.decision_reason!.map((reason, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
                          <span className="shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-indigo-400" />
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

              </div>
            </div>
          )}

          {/* ── Repository Context ── */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <BookOpen className="w-3 h-3" />
              Repository Context
            </h4>
            <div className="bg-white border border-slate-100 rounded-xl p-4 space-y-3">

              {/* Context loaded status */}
              <div className="flex items-center gap-2">
                {review.repository_context_loaded ? (
                  <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-full px-2.5 py-1">
                    ✓ Context Loaded
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 bg-slate-100 border border-slate-200 rounded-full px-2.5 py-1">
                    ✕ Context Missing
                  </span>
                )}
                {(review.available_user_stories?.length ?? 0) > 0 && (
                  <span className="text-xs text-slate-400 bg-indigo-50 border border-indigo-100 rounded-full px-2.5 py-1 font-medium">
                    {review.available_user_stories!.length} User {review.available_user_stories!.length === 1 ? 'Story' : 'Stories'} Available
                  </span>
                )}
              </div>

              {/* Detected user story */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 font-medium w-32 shrink-0">Detected Story:</span>
                {review.detected_user_story ? (
                  <span className="text-xs font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-full px-2.5 py-0.5 font-mono">
                    {review.detected_user_story}
                  </span>
                ) : (
                  <span className="text-xs text-slate-400 italic">No user story detected</span>
                )}
              </div>

              {/* Loaded context files */}
              {(review.loaded_context_files?.length ?? 0) > 0 && (
                <div className="flex items-start gap-2">
                  <span className="text-xs text-slate-500 font-medium w-32 shrink-0 pt-0.5">Loaded Files:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {review.loaded_context_files!.map((f) => (
                      <span key={f} className="text-xs bg-violet-50 text-violet-700 border border-violet-200 rounded-full px-2 py-0.5 font-mono">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </div>

          {/* ── AI Governance Review ── */}
          {review.ai_review && (
            <AIReviewSection aiReview={review.ai_review} />
          )}
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
