'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  GitPullRequest,
  Users,
  AlertTriangle,
  ShieldAlert,
  Activity,
  RefreshCw,
  Zap,
  MessageSquare,
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { RiskCard } from '../components/RiskCard';
import { DeveloperTable, Developer } from '../components/DeveloperTable';
import { ReviewFeed } from '../components/ReviewFeed';
import { Review } from '../components/ReviewCard';
import { HealthScoreCard } from '../components/HealthScoreCard';
import { HotspotTable } from '../components/HotspotTable';
import { TimelineFeed, TimelineEvent } from '../components/TimelineFeed';
import { FindingsSummary } from '../components/FindingsSummary';
import { ContextStatusCard, ContextStatus } from '../components/ContextStatusCard';

const BASE_URL = 'https://review-engine.onrender.com';
const REFRESH_INTERVAL_MS = 10_000;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface OverviewData {
  total_reviews: number;
  total_repositories: number;
  total_developers: number;
  total_findings: number;
  high_risk_reviews: number;
  blocked_reviews: number;
}

interface RiskData {
  LOW: number;
  MEDIUM: number;
  HIGH: number;
}

interface HealthData {
  engineering_health_score: number;
  health_label: string;
}

interface HotspotEntry {
  filename: string;
  modifications: number;
  risk_score: number;
}
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function SectionHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-5">
      <h2 className="text-lg font-bold text-slate-800">{title}</h2>
      {subtitle && <p className="text-sm text-slate-400 mt-0.5">{subtitle}</p>}
    </div>
  );
}

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-2xl border border-slate-100 shadow-sm p-6 ${className}`}>
      {children}
    </div>
  );
}

function Spinner() {
  return (
    <div className="flex items-center justify-center gap-2 text-slate-400 text-sm py-6">
      <RefreshCw className="w-4 h-4 animate-spin" />
      <span>Loading…</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Safe JSON fetcher — returns null on failure instead of throwing
// ---------------------------------------------------------------------------
async function safeFetch<T>(url: string): Promise<T | null> {
  try {
    const r = await fetch(url);
    if (!r.ok) return null;
    return r.json();
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export default function GovernanceDashboard() {
  const [overview, setOverview]             = useState<OverviewData | null>(null);
  const [risks, setRisks]                   = useState<RiskData | null>(null);
  const [health, setHealth]                 = useState<HealthData | null>(null);
  const [developers, setDevelopers]         = useState<Developer[]>([]);
  const [reviews, setReviews]               = useState<Review[]>([]);
  const [hotspots, setHotspots]             = useState<HotspotEntry[]>([]);
  const [timeline, setTimeline]             = useState<TimelineEvent[]>([]);
  const [findingsSummary, setFindingsSummary] = useState<Record<string, number>>({});
  const [summaryText, setSummaryText]       = useState<string>('');
  const [contextStatus, setContextStatus]   = useState<ContextStatus | null>(null);
  const [lastUpdated, setLastUpdated]       = useState<Date | null>(null);
  const [loading, setLoading]               = useState(true);
  const [error, setError]                   = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    const [ov, rk, hl, devs, revs, hs, tl, fs, sm, cs] = await Promise.all([
      safeFetch<OverviewData>(`${BASE_URL}/analytics/overview`),
      safeFetch<RiskData>(`${BASE_URL}/analytics/risks`),
      safeFetch<HealthData>(`${BASE_URL}/analytics/health`),
      safeFetch<Developer[]>(`${BASE_URL}/analytics/developers`),
      safeFetch<Review[]>(`${BASE_URL}/reviews`),
      safeFetch<HotspotEntry[]>(`${BASE_URL}/analytics/hotspots`),
      safeFetch<TimelineEvent[]>(`${BASE_URL}/analytics/timeline`),
      safeFetch<Record<string, number>>(`${BASE_URL}/analytics/findings-summary`),
      safeFetch<{ summary: string }>(`${BASE_URL}/analytics/summary`),
      safeFetch<ContextStatus>(`${BASE_URL}/analytics/context-status`),
    ]);

    if (!ov && !rk) {
      setError('Unable to reach the analytics backend. Retrying…');
    } else {
      setError(null);
    }

    if (ov)   setOverview(ov);
    if (rk)   setRisks(rk);
    if (hl)   setHealth(hl);
    if (devs) setDevelopers(Array.isArray(devs) ? devs : []);
    if (revs) setReviews(Array.isArray(revs) ? revs : []);
    if (hs)   setHotspots(Array.isArray(hs) ? hs : []);
    if (tl)   setTimeline(Array.isArray(tl) ? tl : []);
    if (fs)   setFindingsSummary(fs && typeof fs === 'object' ? fs : {});
    if (sm)   setSummaryText(sm.summary ?? '');
    if (cs)   setContextStatus(cs);

    setLastUpdated(new Date());
    setLoading(false);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchAll();
    const interval = setInterval(fetchAll, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const riskTotal = risks ? risks.LOW + risks.MEDIUM + risks.HIGH : 0;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                              */}
      {/* ------------------------------------------------------------------ */}
      <header className="bg-white border-b border-slate-100 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-violet-600 to-indigo-700 p-2 rounded-xl shadow-md">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 leading-tight">
                Engineering Governance Dashboard
              </h1>
              <p className="text-xs text-slate-400">
                Centralized Engineering Intelligence Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 shrink-0">
            {lastUpdated && (
              <span className="text-xs text-slate-400 hidden sm:block">
                Updated {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            <div className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 rounded-full px-3 py-1">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className="text-xs font-semibold text-emerald-700">Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* Main content                                                        */}
      {/* ------------------------------------------------------------------ */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-10">

        {/* Error banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {/* ---------------------------------------------------------------- */}
        {/* Governance summary banner                                        */}
        {/* ---------------------------------------------------------------- */}
        {!loading && summaryText && (
          <div className="bg-indigo-50 border border-indigo-200 rounded-2xl px-5 py-4 flex items-start gap-3">
            <MessageSquare className="w-4 h-4 text-indigo-500 mt-0.5 shrink-0" />
            <p className="text-sm text-indigo-800 leading-relaxed">{summaryText}</p>
          </div>
        )}

        {/* ---------------------------------------------------------------- */}
        {/* Health score + Overview row                                      */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <SectionHeader
            title="Overview"
            subtitle="Aggregated engineering activity across all repositories"
          />
          {loading ? (
            <Spinner />
          ) : (
            <div className="space-y-4">
              {/* Health score */}
              {health && (
                <HealthScoreCard
                  score={health.engineering_health_score}
                  label={health.health_label}
                />
              )}

              {/* Metric cards */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <MetricCard
                  title="Total Reviews"
                  value={overview?.total_reviews ?? 0}
                  description="All-time review runs"
                  icon={<GitPullRequest />}
                  iconBg="bg-indigo-50"
                  iconColor="text-indigo-600"
                />
                <MetricCard
                  title="Developers"
                  value={overview?.total_developers ?? 0}
                  description="Unique contributors"
                  icon={<Users />}
                  iconBg="bg-violet-50"
                  iconColor="text-violet-600"
                />
                <MetricCard
                  title="Findings"
                  value={overview?.total_findings ?? 0}
                  description="Across all reviews"
                  icon={<AlertTriangle />}
                  iconBg="bg-amber-50"
                  iconColor="text-amber-600"
                />
                <MetricCard
                  title="High Risk"
                  value={overview?.high_risk_reviews ?? 0}
                  description="Require attention"
                  icon={<ShieldAlert />}
                  iconBg="bg-red-50"
                  iconColor="text-red-600"
                />
                <MetricCard
                  title="Blocked"
                  value={overview?.blocked_reviews ?? 0}
                  description="Reviews blocked"
                  icon={<Zap />}
                  iconBg="bg-rose-50"
                  iconColor="text-rose-600"
                />
                <MetricCard
                  title="Repositories"
                  value={overview?.total_repositories ?? 0}
                  description="Under governance"
                  icon={<Activity />}
                  iconBg="bg-teal-50"
                  iconColor="text-teal-600"
                />
              </div>
            </div>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Risk distribution                                                */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <SectionHeader
            title="Risk Distribution"
            subtitle="Review risk breakdown across severity levels"
          />
          {loading ? (
            <Spinner />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <RiskCard level="LOW"    count={risks?.LOW    ?? 0} total={riskTotal} />
              <RiskCard level="MEDIUM" count={risks?.MEDIUM ?? 0} total={riskTotal} />
              <RiskCard level="HIGH"   count={risks?.HIGH   ?? 0} total={riskTotal} />
            </div>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Findings distribution                                            */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <SectionHeader
            title="Findings Distribution"
            subtitle="Breakdown of governance findings by category"
          />
          {loading ? <Spinner /> : <FindingsSummary summary={findingsSummary} />}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Hotspots + Timeline side-by-side on larger screens               */}
        {/* ---------------------------------------------------------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section>
            <SectionHeader
              title="File Hotspots"
              subtitle="Most frequently modified files — top candidates for refactoring"
            />
            <Card>
              {loading ? <Spinner /> : <HotspotTable hotspots={hotspots} />}
            </Card>
          </section>

          <section>
            <SectionHeader
              title="Activity Timeline"
              subtitle="Live chronological engineering events feed"
            />
            <Card className="max-h-[480px] overflow-y-auto">
              {loading ? <Spinner /> : <TimelineFeed events={timeline.slice(0, 20)} />}
            </Card>
          </section>
        </div>

        {/* ---------------------------------------------------------------- */}
        {/* Developer analytics                                              */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <SectionHeader
            title="Developer Analytics"
            subtitle="Per-developer push activity and risk metrics"
          />
          <Card>
            {loading ? <Spinner /> : <DeveloperTable developers={developers} />}
          </Card>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Repository Context Status                                        */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <SectionHeader
            title="Repository Context Status"
            subtitle="Governance context availability across connected repositories"
          />
          {loading ? (
            <Spinner />
          ) : contextStatus ? (
            <ContextStatusCard status={contextStatus} />
          ) : (
            <p className="text-slate-400 text-sm">Context status unavailable.</p>
          )}
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Review history feed                                              */}
        {/* ---------------------------------------------------------------- */}
        <section>
          <SectionHeader
            title="Review History"
            subtitle="Latest code reviews — click a card to expand findings and diffs"
          />
          {loading ? <Spinner /> : <ReviewFeed reviews={reviews} />}
        </section>

      </main>

      {/* ------------------------------------------------------------------ */}
      {/* Footer                                                              */}
      {/* ------------------------------------------------------------------ */}
      <footer className="border-t border-slate-100 mt-12 py-5 text-center text-xs text-slate-400">
        Engineering Governance Dashboard · Auto-refreshes every {REFRESH_INTERVAL_MS / 1000}s
      </footer>
    </div>
  );
}
