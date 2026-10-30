import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  FileCheck2,
  AlertTriangle,
  Clock,
  Search,
  Download,
  RefreshCw,
  PlusCircle,
  Filter,
  BarChart3,
  Layers,
  ArrowUpDown,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Database,
} from 'lucide-react';
import { DashboardStats, DashboardAuditsResponse } from '../types';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [auditsResponse, setAuditsResponse] = useState<DashboardAuditsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingTable, setLoadingTable] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination State
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/v1/dashboard/stats');
      if (!res.ok) throw new Error('Failed to load dashboard statistics.');
      const data: DashboardStats = await res.json();
      setStats(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      }
    }
  };

  const fetchAudits = async () => {
    setLoadingTable(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '10',
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      if (searchTerm.trim()) params.append('search', searchTerm.trim());
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const res = await fetch(`/api/v1/dashboard/audits?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to load audits.');
      const data: DashboardAuditsResponse = await res.json();
      setAuditsResponse(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      }
    } finally {
      setLoadingTable(false);
    }
  };

  useEffect(() => {
    const loadInitial = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchAudits()]);
      setLoading(false);
    };
    loadInitial();
  }, []);

  useEffect(() => {
    fetchAudits();
  }, [page, statusFilter, sortBy, sortOrder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchAudits();
  };

  const handleExportCSV = () => {
    const params = new URLSearchParams();
    if (searchTerm.trim()) params.append('search', searchTerm.trim());
    if (statusFilter !== 'all') params.append('status', statusFilter);
    window.location.href = `/api/v1/dashboard/export?${params.toString()}`;
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
    setPage(1);
  };

  // Find max activity value for chart scaling
  const maxActivity = useMemo(() => {
    if (!stats?.activity_over_time || !stats.activity_over_time.length) return 1;
    return Math.max(...stats.activity_over_time.map((d) => Math.max(d.audits || 0, d.findings || 0)), 1);
  }, [stats]);

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Top Banner / Breadcrumb & Actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#E7E5E4] pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold mb-1">
            <span>Enterprise Reviewer Hub</span>
            <span>•</span>
            <span>Dataset Integrity Operations</span>
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] tracking-tight">
            Reviewer Workspace & Analytics
          </h1>
          <p className="text-xs text-[#78716C] mt-1 max-w-2xl">
            Centralized monitoring for crowd dataset audits, worker duplication clusters, and marker verification.
            All metrics ground directly in empirical database records under strict 7-day retention.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => {
              fetchStats();
              fetchAudits();
            }}
            className="px-3 py-2 rounded-md border border-[#D6D3D1] bg-white text-xs font-medium text-[#1C1917] hover:bg-[#F4EFEA] transition-colors flex items-center gap-1.5 shadow-sm"
            title="Refresh statistics"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[#78716C]" />
            Refresh
          </button>

          <button
            onClick={handleExportCSV}
            className="px-3 py-2 rounded-md border border-[#D6D3D1] bg-white text-xs font-medium text-[#1C1917] hover:bg-[#F4EFEA] transition-colors flex items-center gap-1.5 shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-[#78716C]" />
            Export Summary (CSV)
          </button>

          <Link
            to="/audit"
            className="px-4 py-2 rounded-md bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors flex items-center gap-1.5 shadow-sm"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            New Audit
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-md bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="font-mono hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="canary-card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-[#78716C]">Total Audits</span>
            <div className="w-8 h-8 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center border border-[#E8DEC8]">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="font-editorial text-3xl font-medium text-[#1C1917]">
            {loading ? '...' : stats?.total_audits || 0}
          </div>
          <div className="flex items-center gap-2 text-[11px] font-mono text-[#78716C] pt-1 border-t border-[#F4EFEA]">
            <span className="text-emerald-700 font-semibold">{stats?.completed_audits || 0} completed</span>
            <span>•</span>
            <span className="text-amber-700">{stats?.running_audits || 0} active</span>
          </div>
        </div>

        <div className="canary-card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-[#78716C]">Answers Analyzed</span>
            <div className="w-8 h-8 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center border border-[#E8DEC8]">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="font-editorial text-3xl font-medium text-[#1C1917]">
            {loading ? '...' : stats?.total_answers_analyzed.toLocaleString() || 0}
          </div>
          <div className="text-[11px] font-mono text-[#78716C] pt-1 border-t border-[#F4EFEA]">
            Avg {stats && stats.total_audits > 0 ? Math.round(stats.total_answers_analyzed / stats.total_audits) : 0} answers/audit
          </div>
        </div>

        <div className="canary-card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-[#78716C]">Pending Human Review</span>
            <div className="w-8 h-8 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center border border-[#E8DEC8]">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="font-editorial text-3xl font-medium text-[#1C1917]">
            {loading ? '...' : stats?.findings_requiring_review || 0}
          </div>
          <div className="flex items-center gap-2 text-[11px] font-mono text-[#78716C] pt-1 border-t border-[#F4EFEA]">
            <span className="text-rose-700 font-medium">{stats?.high_confidence_findings || 0} High</span>
            <span>•</span>
            <span className="text-amber-700">{stats?.medium_confidence_findings || 0} Med</span>
            <span>•</span>
            <span>{stats?.low_confidence_findings || 0} Low</span>
          </div>
        </div>

        <div className="canary-card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-[#78716C]">Adjudicated Findings</span>
            <div className="w-8 h-8 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center border border-[#E8DEC8]">
              <FileCheck2 className="w-4 h-4" />
            </div>
          </div>
          <div className="font-editorial text-3xl font-medium text-[#1C1917]">
            {loading ? '...' : stats?.reviewed_findings || 0}
          </div>
          <div className="text-[11px] font-mono text-emerald-700 pt-1 border-t border-[#F4EFEA]">
            Reviewed without automated penalties
          </div>
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Over Time Timeline */}
        <div className="canary-card p-6 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xs font-mono uppercase tracking-wider text-[#1C1917] font-semibold flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#B8860B]" />
                Audit & Finding Activity (Last 14 Days)
              </h2>
              <p className="text-[11px] text-[#78716C] mt-0.5">Empirical daily volume of audits launched and findings flagged.</p>
            </div>
            <div className="flex items-center gap-3 text-[11px] font-mono">
              <span className="flex items-center gap-1.5 text-[#1C1917]">
                <span className="w-2.5 h-2.5 rounded-sm bg-[#1C1917]"></span> Audits
              </span>
              <span className="flex items-center gap-1.5 text-[#B8860B]">
                <span className="w-2.5 h-2.5 rounded-sm bg-[#B8860B]"></span> Findings
              </span>
            </div>
          </div>

          <div className="pt-4 h-44 flex items-end justify-between gap-2 border-b border-[#E7E5E4] pb-2">
            {stats?.activity_over_time.map((day) => {
              const auditHeight = Math.max(Math.round((day.audits / maxActivity) * 120), day.audits > 0 ? 8 : 2);
              const findingHeight = Math.max(Math.round((day.findings / maxActivity) * 120), day.findings > 0 ? 8 : 2);
              const shortDate = day.date.slice(5);

              return (
                <div key={day.date} className="flex-1 flex flex-col items-center gap-1 group relative">
                  {/* Tooltip on hover */}
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-12 z-20 pointer-events-none bg-[#1C1917] text-[#FAF8F5] text-[10px] font-mono p-1.5 rounded shadow whitespace-nowrap">
                    <div>{day.date}</div>
                    <div className="text-[#B8860B]">{day.audits} Audits | {day.findings} Findings</div>
                  </div>

                  <div className="w-full flex items-end justify-center gap-1 h-32">
                    <div
                      style={{ height: `${auditHeight}px` }}
                      className="w-1.5 sm:w-2.5 bg-[#1C1917] rounded-t transition-all group-hover:brightness-125"
                    ></div>
                    <div
                      style={{ height: `${findingHeight}px` }}
                      className="w-1.5 sm:w-2.5 bg-[#B8860B] rounded-t transition-all group-hover:brightness-125"
                    ></div>
                  </div>
                  <span className="text-[10px] font-mono text-[#A8A29E] transform -rotate-45 sm:rotate-0 mt-1">
                    {shortDate}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Breakdown by Evidence Category & Dataset Scale */}
        <div className="canary-card p-6 space-y-6">
          <div>
            <h2 className="text-xs font-mono uppercase tracking-wider text-[#1C1917] font-semibold mb-3 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-[#B8860B]" />
              Findings by Check Category
            </h2>
            <div className="space-y-3">
              {[
                { label: 'Hidden Markers', key: 'marker', color: 'bg-[#B8860B]' },
                { label: 'Reference Similarity', key: 'similarity', color: 'bg-[#1C1917]' },
                { label: 'Duplicate Answers', key: 'duplicates', color: 'bg-[#78716C]' },
                { label: 'Speed Velocity Anomaly', key: 'speed', color: 'bg-[#A8A29E]' },
              ].map((cat) => {
                const count = stats?.findings_by_category[cat.key] || 0;
                const total = Math.max(Object.values(stats?.findings_by_category || {}).reduce((a, b) => a + b, 0), 1);
                const pct = Math.round((count / total) * 100);

                return (
                  <div key={cat.key} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-[#44403C]">{cat.label}</span>
                      <span className="font-mono font-medium text-[#1C1917]">{count} ({pct}%)</span>
                    </div>
                    <div className="w-full h-1.5 bg-[#F4EFEA] rounded-full overflow-hidden">
                      <div className={`h-full ${cat.color}`} style={{ width: `${pct}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-[#E7E5E4]">
            <h2 className="text-xs font-mono uppercase tracking-wider text-[#1C1917] font-semibold mb-3">
              Dataset Size Distribution
            </h2>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              {Object.entries(stats?.dataset_size_distribution || {}).map(([range, count]) => (
                <div key={range} className="p-2 bg-[#FAF7F2] border border-[#E8DEC8] rounded flex justify-between items-center">
                  <span className="text-[#78716C]">{range} rows:</span>
                  <span className="font-bold text-[#1C1917]">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Audits Activity & Management Section */}
      <div className="canary-card overflow-hidden">
        {/* Table Controls Header */}
        <div className="p-5 border-b border-[#E7E5E4] bg-white flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="font-editorial text-xl text-[#1C1917]">Audit Records & Workspaces</h2>
            <p className="text-xs text-[#78716C]">Inspect verified crowd audit logs, active background jobs, and cascading purge states.</p>
          </div>

          <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-2.5">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#A8A29E] absolute left-3 top-3 pointer-events-none" />
              <input
                type="text"
                placeholder="Search dataset name or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs rounded border border-[#D6D3D1] bg-white focus:outline-none focus:ring-1 focus:ring-[#1C1917] w-56"
              />
            </div>

            <div className="flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-[#78716C]" />
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                className="text-xs py-1.5 px-2.5 rounded border border-[#D6D3D1] bg-white text-[#1C1917] focus:outline-none focus:ring-1 focus:ring-[#1C1917]"
              >
                <option value="all">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="running">Running</option>
                <option value="queued">Queued</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            <button
              type="submit"
              className="px-3 py-1.5 rounded bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors"
            >
              Filter
            </button>
          </form>
        </div>

        {/* Audits Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#FAF7F2] border-b border-[#E7E5E4] text-[#78716C] font-mono uppercase text-[11px]">
                <th className="py-3 px-4 font-medium cursor-pointer" onClick={() => handleSort('dataset_name')}>
                  <div className="flex items-center gap-1">
                    Dataset Name
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4 font-medium cursor-pointer" onClick={() => handleSort('status')}>
                  <div className="flex items-center gap-1">
                    Status
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4 font-medium text-right cursor-pointer" onClick={() => handleSort('answers_count')}>
                  <div className="flex items-center justify-end gap-1">
                    Answers
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4 font-medium text-right">Workers</th>
                <th className="py-3 px-4 font-medium text-right">Findings</th>
                <th className="py-3 px-4 font-medium cursor-pointer" onClick={() => handleSort('created_at')}>
                  <div className="flex items-center gap-1">
                    Created At
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4 font-medium">Duration</th>
                <th className="py-3 px-4 font-medium text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E7E5E4] bg-white">
              {loadingTable ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-xs text-[#78716C]">
                    <div className="flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-[#B8860B]" />
                      <span>Loading audits from database...</span>
                    </div>
                  </td>
                </tr>
              ) : auditsResponse && auditsResponse.items.length > 0 ? (
                auditsResponse.items.map((audit) => {
                  const statusColors: Record<string, string> = {
                    completed: 'bg-emerald-50 text-emerald-800 border-emerald-200',
                    running: 'bg-amber-50 text-amber-800 border-amber-200 animate-pulse',
                    queued: 'bg-blue-50 text-blue-800 border-blue-200',
                    failed: 'bg-rose-50 text-rose-800 border-rose-200',
                  };

                  return (
                    <tr key={audit.id} className="hover:bg-[#FAF8F5] transition-colors">
                      <td className="py-3.5 px-4 font-medium text-[#1C1917]">
                        <div className="flex flex-col">
                          <span className="font-semibold text-sm">{audit.dataset_name}</span>
                          <span className="text-[10px] font-mono text-[#A8A29E]">{audit.id}</span>
                        </div>
                      </td>

                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono border ${
                            statusColors[audit.status] || 'bg-gray-50 text-gray-700 border-gray-200'
                          }`}
                        >
                          {audit.status}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-right font-mono font-medium text-[#1C1917]">
                        {audit.answers_count.toLocaleString()}
                      </td>

                      <td className="py-3.5 px-4 text-right font-mono text-[#44403C]">
                        {audit.workers_count}
                        {audit.flagged_workers_count > 0 && (
                          <span className="text-amber-700 text-[11px] block">
                            ({audit.flagged_workers_count} flagged)
                          </span>
                        )}
                      </td>

                      <td className="py-3.5 px-4 text-right font-mono">
                        {audit.findings_count > 0 ? (
                          <span className="px-1.5 py-0.5 rounded bg-rose-50 text-rose-800 border border-rose-200 font-bold">
                            {audit.findings_count}
                          </span>
                        ) : (
                          <span className="text-[#A8A29E]">0</span>
                        )}
                      </td>

                      <td className="py-3.5 px-4 font-mono text-[#78716C] text-[11px]">
                        {new Date(audit.created_at).toLocaleString()}
                      </td>

                      <td className="py-3.5 px-4 font-mono text-[#78716C] text-[11px]">
                        {audit.duration_seconds !== null && audit.duration_seconds !== undefined
                          ? `${audit.duration_seconds}s`
                          : '—'}
                      </td>

                      <td className="py-3.5 px-4 text-center">
                        <Link
                          to={`/results/${audit.id}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[#F4EFEA] hover:bg-[#E8DEC8] text-[#1C1917] font-medium text-xs transition-colors"
                        >
                          <span>Workspace</span>
                          <ExternalLink className="w-3 h-3 text-[#78716C]" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-16 text-center">
                    <div className="max-w-sm mx-auto space-y-3">
                      <div className="w-10 h-10 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mx-auto border border-[#E8DEC8]">
                        <Clock className="w-5 h-5" />
                      </div>
                      <h3 className="font-editorial text-lg text-[#1C1917]">No audit records found</h3>
                      <p className="text-xs text-[#78716C]">
                        {searchTerm || statusFilter !== 'all'
                          ? 'No audits matched your search criteria. Try resetting filters.'
                          : 'You have not uploaded any datasets yet. Launch your first contamination audit to review findings.'}
                      </p>
                      <Link
                        to="/audit"
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors"
                      >
                        <PlusCircle className="w-3.5 h-3.5" />
                        Start New Audit
                      </Link>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {auditsResponse && auditsResponse.total_pages > 1 && (
          <div className="p-4 border-t border-[#E7E5E4] bg-[#FAF8F5] flex items-center justify-between text-xs font-mono text-[#78716C]">
            <div>
              Showing page {auditsResponse.page} of {auditsResponse.total_pages} ({auditsResponse.total} total audits)
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-2.5 py-1 rounded border border-[#D6D3D1] bg-white disabled:opacity-40 hover:bg-[#F4EFEA] transition-colors flex items-center gap-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                Prev
              </button>
              <button
                disabled={page >= auditsResponse.total_pages}
                onClick={() => setPage(page + 1)}
                className="px-2.5 py-1 rounded border border-[#D6D3D1] bg-white disabled:opacity-40 hover:bg-[#F4EFEA] transition-colors flex items-center gap-1"
              >
                Next
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
