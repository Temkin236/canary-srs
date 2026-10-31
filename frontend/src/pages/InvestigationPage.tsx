import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ShieldCheck,
  AlertTriangle,
  Filter,
  CheckCircle2,
  History,
  Trash2,
  Download,
  Loader2,
  Info,
} from 'lucide-react';
import {
  FindingDetailedItem,
  InvestigationWorkspaceResponse,
} from '../types';
import { SideBySideComparisonModal } from '../components/investigation/SideBySideComparisonModal';
import { AdjudicationModal } from '../components/investigation/AdjudicationModal';
import { DatasetQualityView } from '../components/investigation/DatasetQualityView';

export const InvestigationPage: React.FC = () => {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();

  const [data, setData] = useState<InvestigationWorkspaceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Tab State: overview | findings | markers | duplicates | quality | history | privacy
  const [activeTab, setActiveTab] = useState<
    'overview' | 'findings' | 'markers' | 'duplicates' | 'quality' | 'history' | 'privacy'
  >('findings');


  // Findings Filters
  const [confidenceFilter, setConfidenceFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchWorker, setSearchWorker] = useState<string>('');

  // Modals
  const [comparisonFindingId, setComparisonFindingId] = useState<string | null>(null);
  const [adjudicatingFinding, setAdjudicatingFinding] = useState<FindingDetailedItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleted, setDeleted] = useState(false);

  const fetchWorkspace = async () => {
    if (!auditId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/audits/${auditId}/investigate`);
      if (!res.ok) {
        throw new Error('Audit workspace not found or expired under the 7-day retention policy.');
      }
      const json: InvestigationWorkspaceResponse = await res.json();
      setData(json);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred loading investigation workspace.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkspace();
  }, [auditId]);

  const handleUpdateFinding = (updated: FindingDetailedItem) => {
    if (!data) return;
    const newFindings = data.findings.map((f) => (f.id === updated.id ? updated : f));
    setData({ ...data, findings: newFindings });
  };

  const handleImmediateDeletion = async () => {
    if (!data || !window.confirm('Are you sure you want to immediately purge this audit and all associated raw records? This cascading action is irreversible.')) {
      return;
    }
    setIsDeleting(true);
    try {
      const res = await fetch(`/api/v1/audits/${data.audit.id}`, { method: 'DELETE' });
      if (res.ok) {
        setDeleted(true);
      } else {
        throw new Error('Deletion failed.');
      }
    } catch {
      alert('Failed to delete audit.');
    } finally {
      setIsDeleting(false);
    }
  };

  if (deleted) {
    return (
      <div className="max-w-2xl mx-auto py-20 px-4 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-[#10B981]/10 text-[#10B981] flex items-center justify-center mx-auto">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <h2 className="font-editorial text-2xl text-[#1C1917]">Audit Purged Permanently</h2>
        <p className="text-xs text-[#78716C] max-w-md mx-auto">
          All cryptographic digests, worker answers, duplicate clusters, and findings for this audit
          have been erased under Canary&apos;s privacy invariant.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors"
        >
          Return to Reviewer Dashboard
        </Link>
      </div>
    );
  }

  // Filter findings
  const filteredFindings = (data?.findings || []).filter((f) => {
    if (confidenceFilter !== 'all' && f.evidence_confidence.toLowerCase() !== confidenceFilter.toLowerCase()) {
      return false;
    }
    if (categoryFilter !== 'all' && f.check_identifier !== categoryFilter) {
      return false;
    }
    if (statusFilter !== 'all' && f.review_status !== statusFilter) {
      return false;
    }
    if (searchWorker.trim()) {
      const q = searchWorker.toLowerCase();
      if (!f.worker_id.toLowerCase().includes(q) && !f.task_id.toLowerCase().includes(q)) {
        return false;
      }
    }
    return true;
  });

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      {/* Top Breadcrumb & Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#E7E5E4] pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-mono text-[#78716C]">
            <Link to="/dashboard" className="hover:text-[#1C1917] flex items-center gap-1 transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" /> Dashboard
            </Link>
            <span>/</span>
            <span>Investigation Workspace</span>
            <span>/</span>
            <span className="text-[#1C1917] font-semibold">{data?.audit.id || auditId}</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="font-editorial text-2xl sm:text-3xl text-[#1C1917] tracking-tight">
              Evidence Adjudication Workspace
            </h1>
            {data && (
              <span
                className={`px-2.5 py-0.5 rounded-full text-[11px] font-mono uppercase font-semibold ${
                  data.audit.status === 'completed'
                    ? 'bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/20'
                    : 'bg-[#B8860B]/15 text-[#B8860B] border border-[#B8860B]/20'
                }`}
              >
                {data.audit.status}
              </span>
            )}
          </div>
          <p className="text-xs text-[#78716C]">
            Dataset: <span className="font-mono text-[#1C1917] font-medium">{data?.audit.dataset_name || '—'}</span>{' '}
            • Retention expires: {data ? new Date(data.audit.expires_at).toLocaleDateString() : '—'}
          </p>
        </div>

        {/* Global Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('privacy')}
            className="px-3 py-1.5 rounded border border-[#D6D3D1] bg-white text-xs font-medium text-[#1C1917] hover:bg-[#FAF8F5] transition-colors flex items-center gap-1.5 shadow-sm"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-[#B8860B]" />
            Privacy & Purge
          </button>
          <a
            href={`/api/v1/audits/${data?.audit.id}/export/csv`}
            download
            className="px-3 py-1.5 rounded bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors flex items-center gap-1.5 shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            Export Evidence
          </a>
        </div>
      </div>

      {/* Workspace Navigation Tabs */}
      <div className="flex items-center border-b border-[#E7E5E4] overflow-x-auto space-x-1 sm:space-x-2 text-xs font-medium">
        {[
          { id: 'findings', label: 'Findings Adjudication', count: data?.findings.length },
          { id: 'overview', label: 'Overview & Metadata' },
          { id: 'quality', label: 'Dataset Quality' },
          { id: 'markers', label: 'Marker Verification', count: data?.markers.length },
          { id: 'duplicates', label: 'Duplicate Clusters', count: data?.duplicate_clusters.length },
          { id: 'history', label: 'Review History' },
          { id: 'privacy', label: 'Privacy & Retention' },
        ].map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3.5 py-2.5 border-b-2 font-mono whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                isActive
                  ? 'border-[#1C1917] text-[#1C1917] font-semibold'
                  : 'border-transparent text-[#78716C] hover:text-[#1C1917] hover:border-[#D6D3D1]'
              }`}
            >
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                    isActive ? 'bg-[#1C1917] text-[#FAF8F5]' : 'bg-[#E7E5E4] text-[#44403C]'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="py-24 text-center space-y-3 text-[#78716C]">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-[#B8860B]" />
          <p className="text-xs font-mono">Loading investigation artifacts and evidence...</p>
        </div>
      ) : error ? (
        <div className="p-6 rounded-lg bg-[#DC2626]/10 border border-[#DC2626]/20 text-[#DC2626] text-xs space-y-3 max-w-lg mx-auto">
          <div className="flex items-center gap-2 font-semibold">
            <AlertTriangle className="w-4 h-4" />
            <span>Workspace Loading Error</span>
          </div>
          <p>{error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-3 py-1.5 rounded bg-[#DC2626] text-white text-xs font-medium hover:bg-[#B91C1C] transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      ) : data ? (
        <>
          {/* TAB 1: FINDINGS ADJUDICATION */}
          {activeTab === 'findings' && (
            <div className="space-y-4">
              {/* Filter Bar */}
              <div className="p-4 rounded-lg bg-white border border-[#E7E5E4] flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <Filter className="w-3.5 h-3.5 text-[#78716C]" />
                    <span className="font-mono text-[#78716C] uppercase tracking-wider text-[11px]">Filters:</span>
                  </div>

                  {/* Confidence */}
                  <select
                    value={confidenceFilter}
                    onChange={(e) => setConfidenceFilter(e.target.value)}
                    className="py-1 px-2.5 rounded border border-[#D6D3D1] bg-white text-xs"
                  >
                    <option value="all">All Confidence</option>
                    <option value="high">High Confidence</option>
                    <option value="medium">Medium Confidence</option>
                    <option value="low">Low Confidence</option>
                  </select>

                  {/* Category */}
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="py-1 px-2.5 rounded border border-[#D6D3D1] bg-white text-xs"
                  >
                    <option value="all">All Check Categories</option>
                    <option value="marker">Marker Detection</option>
                    <option value="similarity">Similarity Comparison</option>
                    <option value="duplicates">Worker Duplicates</option>
                    <option value="speed">Velocity Checks</option>
                  </select>

                  {/* Review Status */}
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="py-1 px-2.5 rounded border border-[#D6D3D1] bg-white text-xs"
                  >
                    <option value="all">All Review Statuses</option>
                    <option value="pending_review">Pending Review</option>
                    <option value="under_review">Under Review</option>
                    <option value="reviewed">Reviewed</option>
                    <option value="dismissed">Dismissed</option>
                    <option value="needs_investigation">Needs Follow-Up</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="Filter task or worker ID..."
                    value={searchWorker}
                    onChange={(e) => setSearchWorker(e.target.value)}
                    className="px-3 py-1 rounded border border-[#D6D3D1] text-xs w-48"
                  />
                  <span className="font-mono text-[11px] text-[#78716C]">
                    {filteredFindings.length} of {data.findings.length} findings
                  </span>
                </div>
              </div>

              {/* Invariant Banner */}
              <div className="p-3 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-between text-xs text-[#78716C]">
                <div className="flex items-center gap-2">
                  <Info className="w-4 h-4 text-[#B8860B] shrink-0" />
                  <span>
                    <strong>Human Review Invariant:</strong> Findings present calibrated empirical evidence.
                    They do not prove automated fraud or cheating.
                  </span>
                </div>
                <span className="text-[10px] font-mono text-[#B8860B]">No Auto-Punishment</span>
              </div>

              {/* Findings Table */}
              <div className="border border-[#E7E5E4] rounded-lg bg-white overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-[#E7E5E4] bg-[#FAF8F5] text-[11px] font-mono text-[#78716C] uppercase tracking-wider">
                        <th className="py-3 px-4">Task & Worker</th>
                        <th className="py-3 px-4">Check Category</th>
                        <th className="py-3 px-4">Confidence</th>
                        <th className="py-3 px-4">Explanation & Evidence</th>
                        <th className="py-3 px-4">Adjudication Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E7E5E4] text-xs">
                      {filteredFindings.length > 0 ? (
                        filteredFindings.map((f) => (
                          <tr key={f.id} className="hover:bg-[#FAF8F5]/80 transition-colors">
                            <td className="py-3.5 px-4 font-mono">
                              <div className="font-semibold text-[#1C1917]">{f.task_id}</div>
                              <div className="text-[11px] text-[#78716C]">Worker: {f.worker_id}</div>
                            </td>
                            <td className="py-3.5 px-4 font-mono">
                              <span className="px-2 py-0.5 rounded bg-[#FAF5EE] text-[#B8860B] border border-[#E8DEC8] text-[10px]">
                                {f.check_identifier}
                              </span>
                              <div className="text-[10px] text-[#78716C] mt-0.5">{f.finding_type}</div>
                            </td>
                            <td className="py-3.5 px-4 font-mono">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                                  f.evidence_confidence === 'High'
                                    ? 'bg-[#DC2626]/10 text-[#DC2626] border border-[#DC2626]/20'
                                    : f.evidence_confidence === 'Medium'
                                    ? 'bg-[#B8860B]/15 text-[#B8860B] border border-[#B8860B]/20'
                                    : 'bg-[#2563EB]/10 text-[#2563EB] border border-[#2563EB]/20'
                                }`}
                              >
                                {f.evidence_confidence}
                              </span>
                            </td>
                            <td className="py-3.5 px-4 max-w-md">
                              <p className="text-xs text-[#1C1917] leading-relaxed line-clamp-2">{f.explanation}</p>
                              {f.evidence_text && (
                                <p className="text-[11px] font-mono text-[#78716C] mt-1 bg-[#FAF8F5] p-1.5 rounded border border-[#E7E5E4] truncate">
                                  {f.evidence_text}
                                </p>
                              )}
                            </td>
                            <td className="py-3.5 px-4 font-mono">
                              <span
                                className={`px-2 py-1 rounded text-[10px] font-semibold inline-block ${
                                  f.review_status === 'reviewed'
                                    ? 'bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/25'
                                    : f.review_status === 'dismissed'
                                    ? 'bg-[#78716C]/15 text-[#78716C] border border-[#78716C]/25'
                                    : f.review_status === 'under_review'
                                    ? 'bg-[#2563EB]/15 text-[#2563EB] border border-[#2563EB]/25'
                                    : f.review_status === 'needs_investigation'
                                    ? 'bg-[#EA580C]/15 text-[#EA580C] border border-[#EA580C]/25'
                                    : 'bg-[#FAF5EE] text-[#B8860B] border border-[#E8DEC8]'
                                }`}
                              >
                                {f.review_status.replace(/_/g, ' ')}
                              </span>
                              {f.assigned_reviewer && (
                                <div className="text-[10px] text-[#78716C] mt-1">
                                  Assigned: {f.assigned_reviewer}
                                </div>
                              )}
                            </td>
                            <td className="py-3.5 px-4 text-right space-x-1.5 whitespace-nowrap">
                              <button
                                onClick={() => setComparisonFindingId(f.id)}
                                className="px-2.5 py-1 rounded border border-[#D6D3D1] bg-white text-[#1C1917] hover:bg-[#FAF8F5] text-xs font-mono transition-colors"
                                title="Open side-by-side comparison"
                              >
                                Compare
                              </button>
                              <button
                                onClick={() => setAdjudicatingFinding(f)}
                                className="px-2.5 py-1 rounded bg-[#1C1917] text-[#FAF8F5] hover:bg-[#292524] text-xs font-mono transition-colors"
                              >
                                Adjudicate
                              </button>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={6} className="py-12 text-center text-[#78716C] text-xs font-mono">
                            No findings match your current filter criteria.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: OVERVIEW & METADATA */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="canary-card p-4 space-y-1">
                  <span className="text-[11px] font-mono uppercase text-[#78716C]">Total Answers</span>
                  <div className="font-editorial text-2xl text-[#1C1917]">{data.audit.answers_count}</div>
                  <div className="text-[11px] text-[#78716C]">Across {data.audit.workers_count} crowd workers</div>
                </div>
                <div className="canary-card p-4 space-y-1">
                  <span className="text-[11px] font-mono uppercase text-[#78716C]">Flagged Workers</span>
                  <div className="font-editorial text-2xl text-[#B8860B]">{data.audit.flagged_workers_count}</div>
                  <div className="text-[11px] text-[#78716C]">Requiring human review</div>
                </div>
                <div className="canary-card p-4 space-y-1">
                  <span className="text-[11px] font-mono uppercase text-[#78716C]">External AI Consent</span>
                  <div className="font-editorial text-2xl text-[#1C1917]">
                    {data.audit.consent_external_ai ? 'Granted' : 'Offline Mode'}
                  </div>
                  <div className="text-[11px] text-[#78716C]">Zero data transmitted externally</div>
                </div>
                <div className="canary-card p-4 space-y-1">
                  <span className="text-[11px] font-mono uppercase text-[#78716C]">Retention Countdown</span>
                  <div className="font-editorial text-2xl text-[#10B981]">7 Days</div>
                  <div className="text-[11px] text-[#78716C]">Expires {new Date(data.audit.expires_at).toLocaleDateString()}</div>
                </div>
              </div>

              {/* Calibration telemetry */}
              {data.calibration && (
                <div className="canary-card p-5 space-y-3">
                  <h3 className="font-editorial text-lg text-[#1C1917]">Statistical Calibration & Wilson CI</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
                    <div className="p-3 rounded bg-[#FAF8F5] border border-[#E7E5E4]">
                      <span className="text-[#78716C] block">Sample Size</span>
                      <span className="text-sm font-semibold text-[#1C1917]">{data.calibration.sample_size} answers</span>
                    </div>
                    <div className="p-3 rounded bg-[#FAF8F5] border border-[#E7E5E4]">
                      <span className="text-[#78716C] block">Estimated FP Rate</span>
                      <span className="text-sm font-semibold text-[#1C1917]">
                        {(data.calibration.estimated_fp_rate * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div className="p-3 rounded bg-[#FAF8F5] border border-[#E7E5E4]">
                      <span className="text-[#78716C] block">Wilson 95% CI Lower</span>
                      <span className="text-sm font-semibold text-[#1C1917]">
                        {(data.calibration.ci_lower * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div className="p-3 rounded bg-[#FAF8F5] border border-[#E7E5E4]">
                      <span className="text-[#78716C] block">Wilson 95% CI Upper</span>
                      <span className="text-sm font-semibold text-[#1C1917]">
                        {(data.calibration.ci_upper * 100).toFixed(2)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB: DATASET QUALITY ANALYTICS */}
          {activeTab === 'quality' && (
            <DatasetQualityView auditId={data.audit.id} />
          )}

          {/* TAB 3: MARKER VERIFICATION */}
          {activeTab === 'markers' && (
            <div className="space-y-4">
              <div className="p-3.5 rounded bg-[#FAF5EE] border border-[#E8DEC8] text-xs text-[#78716C]">
                <strong>Marker Verification Security:</strong> Task markers are seeded into task instructions.
                Canary checks whether workers echoed hidden canary strings or whether markers were stripped.
              </div>

              <div className="border border-[#E7E5E4] rounded-lg bg-white overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#FAF8F5] border-b border-[#E7E5E4] text-[11px] font-mono text-[#78716C] uppercase">
                    <tr>
                      <th className="py-3 px-4">Task ID</th>
                      <th className="py-3 px-4">Expected Marker</th>
                      <th className="py-3 px-4">Detection Status</th>
                      <th className="py-3 px-4">Answer Offset</th>
                      <th className="py-3 px-4">Preparation Version</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E7E5E4] font-mono">
                    {data.markers.map((m) => (
                      <tr key={m.id} className="hover:bg-[#FAF8F5]">
                        <td className="py-3 px-4 font-semibold text-[#1C1917]">{m.task_id}</td>
                        <td className="py-3 px-4 text-[#78716C]">{m.expected_marker}</td>
                        <td className="py-3 px-4">
                          {m.detected ? (
                            <span className="px-2 py-0.5 rounded bg-[#DC2626]/10 text-[#DC2626] font-semibold">
                              Echoed in Answer
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded bg-[#10B981]/10 text-[#10B981]">
                              Not Echoed
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-[#78716C]">
                          {m.location_in_answer ? `[${m.location_in_answer.join(', ')}]` : 'None'}
                        </td>
                        <td className="py-3 px-4 text-[#78716C]">{m.preparation_version}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: DUPLICATE CLUSTERS */}
          {activeTab === 'duplicates' && (
            <div className="space-y-4">
              <div className="p-3.5 rounded bg-[#FAF5EE] border border-[#E8DEC8] text-xs text-[#78716C]">
                <strong>Cross-Worker Near-Duplicate Analysis:</strong> Identifies worker accounts submitting near-identical
                responses on the same task. Demonstrates duplicate clusters without asserting misconduct verdicts.
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.duplicate_clusters.length > 0 ? (
                  data.duplicate_clusters.map((c) => (
                    <div key={c.cluster_id} className="canary-card p-4 space-y-3">
                      <div className="flex items-center justify-between border-b border-[#E7E5E4] pb-2">
                        <span className="font-mono text-xs font-semibold text-[#1C1917]">{c.cluster_id}</span>
                        <span className="text-[10px] font-mono text-[#B8860B] bg-[#FAF5EE] px-2 py-0.5 rounded border border-[#E8DEC8]">
                          Task: {c.task_id}
                        </span>
                      </div>
                      <div className="text-xs space-y-1">
                        <div className="font-mono text-[11px] text-[#78716C]">
                          Involved Workers: {c.worker_ids.join(', ')}
                        </div>
                        <p className="text-xs text-[#44403C] line-clamp-3 bg-[#FAF8F5] p-2 rounded font-mono border border-[#E7E5E4]">
                          {c.representative_text}
                        </p>
                      </div>
                      <div className="flex items-center justify-between text-[11px] font-mono text-[#78716C] pt-1">
                        <span>{c.findings_count} associated findings</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="col-span-2 py-12 text-center text-xs font-mono text-[#78716C]">
                    No cross-worker duplicate clusters detected in this audit.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 5: AUDIT TRAIL / REVIEW HISTORY */}
          {activeTab === 'history' && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-white border border-[#E7E5E4] space-y-3">
                <div className="flex items-center gap-2 font-editorial text-lg text-[#1C1917]">
                  <History className="w-4 h-4 text-[#B8860B]" />
                  <span>Stewardship Adjudication Trail</span>
                </div>
                <div className="space-y-2">
                  {data.findings.flatMap((f) => f.history).length > 0 ? (
                    data.findings
                      .flatMap((f) =>
                        f.history.map((h) => ({ ...h, task_id: f.task_id, worker_id: f.worker_id }))
                      )
                      .sort(
                        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                      )
                      .map((h) => (
                        <div key={h.id} className="p-3 rounded bg-[#FAF8F5] border border-[#E7E5E4] text-xs space-y-1">
                          <div className="flex items-center justify-between text-[11px] font-mono text-[#78716C]">
                            <span className="font-semibold text-[#1C1917]">{h.reviewer_id}</span>
                            <span>{new Date(h.created_at).toLocaleString()}</span>
                          </div>
                          <div className="text-xs">
                            Updated task <span className="font-mono font-medium">{h.task_id}</span> (worker:{' '}
                            <span className="font-mono">{h.worker_id}</span>): status changed from{' '}
                            <span className="font-mono text-[#78716C]">{h.previous_status}</span> to{' '}
                            <span className="font-mono font-semibold text-[#1C1917]">{h.new_status}</span>
                          </div>
                          {h.notes && (
                            <p className="text-[11px] font-mono text-[#44403C] mt-1 bg-white p-2 rounded border border-[#E7E5E4]">
                              {h.notes}
                            </p>
                          )}
                          {h.dismissal_reason && (
                            <p className="text-[11px] font-mono text-[#DC2626] bg-[#DC2626]/5 p-1 rounded">
                              Dismissal Reason: {h.dismissal_reason}
                            </p>
                          )}
                        </div>
                      ))
                  ) : (
                    <div className="py-8 text-center text-xs font-mono text-[#78716C]">
                      No reviewer adjudications recorded yet for this audit.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: PRIVACY & DELETION */}
          {activeTab === 'privacy' && (
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="canary-card p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#DC2626]/10 text-[#DC2626] flex items-center justify-center">
                    <Trash2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-editorial text-lg text-[#1C1917]">Immediate Cascading Purge</h3>
                    <p className="text-xs text-[#78716C]">
                      Erase this dataset and all associated artifacts immediately.
                    </p>
                  </div>
                </div>

                <div className="p-3.5 rounded bg-[#FAF5EE] border border-[#E8DEC8] text-xs text-[#78716C] space-y-1">
                  <span className="font-semibold text-[#1C1917]">Guaranteed Privacy Invariant:</span>
                  <p>
                    Triggering immediate deletion cascades across all database tables, removing raw worker answers,
                    markers, check results, findings, and review history.
                  </p>
                </div>

                <button
                  onClick={handleImmediateDeletion}
                  disabled={isDeleting}
                  className="w-full py-2.5 rounded bg-[#DC2626] text-white text-xs font-semibold hover:bg-[#B91C1C] transition-colors flex items-center justify-center gap-2 shadow-sm"
                >
                  {isDeleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                  Confirm Permanent Immediate Deletion
                </button>
              </div>
            </div>
          )}
        </>
      ) : null}

      {/* Side-by-Side Diff Modal */}
      {comparisonFindingId && (
        <SideBySideComparisonModal
          findingId={comparisonFindingId}
          onClose={() => setComparisonFindingId(null)}
        />
      )}

      {/* Adjudication Modal */}
      {adjudicatingFinding && (
        <AdjudicationModal
          finding={adjudicatingFinding}
          onClose={() => setAdjudicatingFinding(null)}
          onUpdate={handleUpdateFinding}
        />
      )}
    </div>
  );
};
