'use client';

/**
 * AIReviewSection — renders the GPT-5.1 governance review results inside a
 * ReviewCard. Handles both successful and failed AI review payloads.
 */

import { Sparkles, ShieldAlert, GitBranch, Lightbulb, AlertCircle } from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AIReviewResult {
  // Success shape
  ai_summary?: string;
  coverage_percentage?: number;
  missing_requirements?: string[];
  security_review?: string[];
  architecture_review?: string[];
  recommendations?: string[];
  // Failure shape
  status?: string;
  message?: string;
}

interface AIReviewSectionProps {
  aiReview: AIReviewResult;
}

// ---------------------------------------------------------------------------
// Coverage bar helpers
// ---------------------------------------------------------------------------

function coverageColor(pct: number): string {
  if (pct >= 80) return 'bg-emerald-500';
  if (pct >= 50) return 'bg-amber-400';
  return 'bg-red-500';
}

function coverageTextColor(pct: number): string {
  if (pct >= 80) return 'text-emerald-700';
  if (pct >= 50) return 'text-amber-600';
  return 'text-red-600';
}

function coverageBgColor(pct: number): string {
  if (pct >= 80) return 'bg-emerald-50 border-emerald-200';
  if (pct >= 50) return 'bg-amber-50 border-amber-200';
  return 'bg-red-50 border-red-200';
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function CoverageBar({ pct }: { pct: number }) {
  const clamped = Math.min(100, Math.max(0, pct));
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${coverageColor(clamped)}`}
          style={{ width: `${clamped}%` }}
        />
      </div>
      <span className={`text-xs font-bold w-10 text-right ${coverageTextColor(clamped)}`}>
        {clamped}%
      </span>
    </div>
  );
}

function BulletList({ items, emptyText }: { items: string[]; emptyText: string }) {
  if (!items || items.length === 0) {
    return <p className="text-xs text-slate-400 italic">{emptyText}</p>;
  }
  return (
    <ul className="space-y-1">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
          <span className="mt-0.5 shrink-0 w-1.5 h-1.5 rounded-full bg-slate-400" />
          {item}
        </li>
      ))}
    </ul>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function AIReviewSection({ aiReview }: AIReviewSectionProps) {
  // --- Failure / unavailable state ---
  if (!aiReview || aiReview.status === 'failed' || aiReview.message) {
    return (
      <div className="flex items-center gap-2 pt-1 border-t border-slate-100">
        <AlertCircle className="w-3 h-3 text-slate-300" />
        <span className="text-xs text-slate-400 italic">
          {aiReview?.message ?? 'AI Governance Review unavailable'}
        </span>
      </div>
    );
  }

  const {
    ai_summary = '',
    coverage_percentage = 0,
    missing_requirements = [],
    security_review = [],
    architecture_review = [],
    recommendations = [],
  } = aiReview;

  return (
    <div className="space-y-4">
      {/* Header */}
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
        <Sparkles className="w-3 h-3 text-amber-400" />
        AI Governance Review
      </h4>

      <div className="bg-white border border-slate-100 rounded-xl p-4 space-y-4">

        {/* AI Summary */}
        {ai_summary && (
          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1">Summary</p>
            <p className="text-xs text-slate-700 leading-relaxed">{ai_summary}</p>
          </div>
        )}

        {/* Coverage */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-semibold text-slate-500">User Story Coverage</p>
            <span
              className={`text-xs font-bold px-2 py-0.5 rounded-full border ${coverageBgColor(coverage_percentage)} ${coverageTextColor(coverage_percentage)}`}
            >
              {coverage_percentage}%
            </span>
          </div>
          <CoverageBar pct={coverage_percentage} />
        </div>

        {/* Missing Requirements */}
        {missing_requirements.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1 flex items-center gap-1">
              <AlertCircle className="w-3 h-3 text-amber-500" />
              Missing Requirements
            </p>
            <BulletList items={missing_requirements} emptyText="None detected" />
          </div>
        )}

        {/* Security Review */}
        {security_review.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1 flex items-center gap-1">
              <ShieldAlert className="w-3 h-3 text-red-500" />
              Security Observations
            </p>
            <BulletList items={security_review} emptyText="No concerns" />
          </div>
        )}

        {/* Architecture Review */}
        {architecture_review.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1 flex items-center gap-1">
              <GitBranch className="w-3 h-3 text-indigo-500" />
              Architecture Review
            </p>
            <BulletList items={architecture_review} emptyText="No concerns" />
          </div>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1 flex items-center gap-1">
              <Lightbulb className="w-3 h-3 text-yellow-500" />
              Recommendations
            </p>
            <ul className="space-y-1">
              {recommendations.map((rec, i) => (
                <li
                  key={i}
                  className="text-xs text-slate-700 bg-slate-50 border border-slate-100 rounded-lg px-3 py-1.5 flex items-start gap-2"
                >
                  <span className="shrink-0 mt-0.5 text-yellow-500">→</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
