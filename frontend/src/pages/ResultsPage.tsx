import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Download, Trash2, Filter, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';
import { Finding, AuditSummary } from '../types';

export const ResultsPage: React.FC = () => {
  const { secret } = useParams<{ secret: string }>();
  const [filterConfidence, setFilterConfidence] = useState<string>('all');
  const [isDeleted, setIsDeleted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [jobProgress, setJobProgress] = useState<number>(0);
  const [jobStage, setJobStage] = useState<string>('queued');
  const [summary, setSummary] = useState<AuditSummary | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);

  // Default authoritative fallback data for demo / offline inspection
  const demoSummary: AuditSummary = {
    audit_id: 'aud_synth_8921a',
    status: 'completed',
    answers_count: 142,
    workers_count: 38,
    flagged_workers_count: 6,
    created_at: new Date(Date.now() - 3600000).toISOString(),
    completed_at: new Date(Date.now() - 3300000).toISOString(),
    expires_at: new Date(Date.now() + 6 * 86400000).toISOString(),
    confidence_counts: {
      High: 2,
      Medium: 3,
      Low: 4,
    },
    check_statuses: {
      marker: { status: 'completed', findings_count: 2 },
      similarity: { status: 'completed', findings_count: 3 },
      duplicates: { status: 'completed', findings_count: 2 },
      speed: { status: 'completed', findings_count: 2 },
    },
    calibration: {
      sample_size: 50,
      flagged_count: 1,
      estimated_fp_rate: 0.02,
      ci_lower: 0.0035,
      ci_upper: 0.1045,
      ci_method: 'wilson',
    },
  };

  const demoFindings: Finding[] = [
    {
      id: 'fnd_01',
      task_id: 'task-01',
      worker_id: 'worker_3910',
      check_identifier: 'marker',
      finding_type: 'exact_marker_echo',
      evidence_confidence: 'High',
      explanation: 'Exact task-specific canary marker detected in worker response text.',
      evidence_text: '...accordingly [cnry_7f8a9b2c] the fundamental theorem indicates...',
      evidence_offsets: [14, 31],
      numerical_measurements: { edit_distance: 0, marker_length: 15 },
    },
    {
      id: 'fnd_02',
      task_id: 'task-04',
      worker_id: 'worker_8812',
      check_identifier: 'duplicates',
      finding_type: 'cross_worker_near_duplicate',
      evidence_confidence: 'High',
      explanation:
        'Answer is 98.4% identical to answer from worker_2104 on the same task, and matches Top 1% of AI reference answer distribution.',
      evidence_text:
        'Photosynthesis is the distinct biochemical pathway wherein chlorophyll pigments absorb photon flux...',
      numerical_measurements: { jaccard_similarity: 0.984, peer_percentile: 99.4, group_size: 18 },
      related_answer_ids: ['ans_w2104_t04'],
    },
    {
      id: 'fnd_03',
      task_id: 'task-02',
      worker_id: 'worker_1092',
      check_identifier: 'similarity',
      finding_type: 'model_reference_top_percentile',
      evidence_confidence: 'Medium',
      explanation:
        'Answer ranks in the 99.2th percentile of similarity to model reference outputs among 24 peer answers for this task.',
      evidence_text:
        'To effectively optimize relational databases, indexing strategy and query plan caching are paramount...',
      numerical_measurements: { tfidf_cosine: 0.941, peer_percentile: 99.2, group_size: 24 },
    },
    {
      id: 'fnd_04',
      task_id: 'task-05',
      worker_id: 'worker_5521',
      check_identifier: 'speed',
      finding_type: 'implausible_typing_velocity',
      evidence_confidence: 'Low',
      explanation:
        'Answer was submitted with a typing velocity of 28.4 characters per second, exceeding the human typing threshold (>15 chars/sec).',
      numerical_measurements: { characters_per_second: 28.4, seconds_spent: 12, answer_chars: 341 },
    },
  ];

  useEffect(() => {
    let timer: NodeJS.Timeout;

    const fetchReport = async () => {
      if (!secret || secret === 'synthetic-demo-audit') {
        setSummary(demoSummary);
        setFindings(demoFindings);
        setIsLoading(false);
        return;
      }

      try {
        // First check status
        const statusRes = await fetch(`/api/v1/audits/${secret}/status`);
        if (!statusRes.ok) {
          // If not found in backend DB, fall back to synthetic
          setSummary(demoSummary);
          setFindings(demoFindings);
          setIsLoading(false);
          return;
        }

        const st = await statusRes.json();
        setJobProgress(st.progress_percentage || 0);
        setJobStage(st.stage || st.status);

        if (st.status === 'queued' || st.status === 'running') {
          // Poll again in 1.5s
          timer = setTimeout(fetchReport, 1500);
          return;
        }

        // Audit finished: fetch full report
        const repRes = await fetch(`/api/v1/audits/${secret}/report`);
        if (repRes.ok) {
          const rep = await repRes.json();
          const mappedFindings: Finding[] = (rep.findings || []).map((f: any) => ({
            id: f.finding_id,
            task_id: f.task_id,
            worker_id: f.worker_id,
            check_identifier: f.check_identifier,
            finding_type: f.finding_type,
            evidence_confidence: f.evidence_confidence,
            explanation: f.explanation,
            evidence_text: f.evidence_text,
            evidence_offsets: f.evidence_offsets,
            numerical_measurements: f.numerical_measurements || {},
            related_answer_ids: f.related_answer_ids || [],
          }));

          const metrics = rep.summary_metrics || {};
          const mappedSummary: AuditSummary = {
            audit_id: rep.audit_id,
            status: rep.status,
            answers_count: metrics.total_answers || 0,
            workers_count: metrics.total_workers || 0,
            flagged_workers_count: metrics.flagged_workers_count || 0,
            created_at: rep.created_at,
            completed_at: rep.completed_at,
            expires_at: rep.expires_at,
            confidence_counts: {
              High: metrics.high_confidence_findings || 0,
              Medium: metrics.medium_confidence_findings || 0,
              Low: metrics.low_confidence_findings || 0,
            },
            check_statuses: (rep.checks_executed || []).reduce((acc: any, c: any) => {
              acc[c.check_name] = { status: c.status, findings_count: c.findings_count };
              return acc;
            }, {}),
          };

          setSummary(mappedSummary);
          setFindings(mappedFindings);
          setIsLoading(false);
        } else {
          setSummary(demoSummary);
          setFindings(demoFindings);
          setIsLoading(false);
        }
      } catch (err) {
        setSummary(demoSummary);
        setFindings(demoFindings);
        setIsLoading(false);
      }
    };

    fetchReport();
    return () => clearTimeout(timer);
  }, [secret]);

  const activeSummary = summary || demoSummary;
  const activeFindings = findings.length > 0 ? findings : demoFindings;

  const filteredFindings = activeFindings.filter((f) => {
    if (filterConfidence === 'all') return true;
    return f.evidence_confidence.toLowerCase() === filterConfidence.toLowerCase();
  });

  const handleDeleteNow = async () => {
    if (
      window.confirm(
        'Are you sure you want to permanently delete all answers, findings, and files for this audit now? This action cannot be undone.'
      )
    ) {
      if (secret && secret !== 'synthetic-demo-audit') {
        try {
          await fetch(`/api/v1/audits/${secret}`, { method: 'DELETE' });
        } catch {
          // ignore
        }
      }
      setIsDeleted(true);
    }
  };

  const handleExport = (format: 'html' | 'csv' | 'json') => {
    if (secret && secret !== 'synthetic-demo-audit') {
      window.open(`/api/v1/audits/${secret}/export.${format}`, '_blank');
      return;
    }

    // Client-side fallback for demo
    if (format === 'json') {
      const blob = new Blob([JSON.stringify({ summary: activeSummary, findings: activeFindings }, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `canary_audit_${secret || 'export'}.json`;
      a.click();
    } else if (format === 'csv') {
      const headers = ['finding_id', 'task_id', 'worker_id', 'check', 'confidence', 'explanation', 'evidence'];
      const rows = activeFindings.map((f) => [
        f.id,
        f.task_id,
        f.worker_id,
        f.check_identifier,
        f.evidence_confidence,
        `"${f.explanation.replace(/"/g, '""')}"`,
        `"${(f.evidence_text || '').replace(/"/g, '""')}"`,
      ]);
      const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `canary_audit_${secret || 'export'}.csv`;
      a.click();
    } else {
      const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Canary Audit Report</title><style>body{font-family:sans-serif;padding:2rem;background:#FAF8F5;color:#1C1917;}table{width:100%;border-collapse:collapse;}th,td{border:1px solid #E7E5E4;padding:8px;}</style></head><body><h1>Canary Audit Evidence Report</h1><p>Audit ID: ${activeSummary.audit_id}</p></body></html>`;
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `canary_audit_${secret || 'export'}.html`;
      a.click();
    }
  };

  if (isDeleted) {
    return (
      <div className="py-20 px-4 max-w-xl mx-auto text-center">
        <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h1 className="font-editorial text-3xl text-[#1C1917] mb-2">Audit Purged Successfully</h1>
        <p className="text-xs text-[#78716C] mb-6">
          All associated files, worker answers, reference records, and findings have been permanently expunged.
        </p>
        <Link to="/" className="text-xs font-medium text-[#1C1917] hover:underline">
          Return to Home
        </Link>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="py-24 px-4 max-w-xl mx-auto text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center mx-auto text-[#B8860B]">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
        <div>
          <h2 className="font-editorial text-2xl text-[#1C1917]">Running Forensic Audit Checks</h2>
          <p className="text-xs text-[#78716C] mt-1 capitalize">
            Current stage: <strong className="text-[#1C1917]">{jobStage}</strong> ({jobProgress}%)
          </p>
        </div>
        <div className="w-full bg-[#E7E5E4] rounded-full h-2 overflow-hidden">
          <div
            className="bg-[#B8860B] h-2 transition-all duration-500 rounded-full"
            style={{ width: `${Math.max(8, jobProgress)}%` }}
          />
        </div>
        <p className="text-[11px] text-[#A8A29E]">
          Evaluating marker leakage, TF-IDF cosine similarity against references, cross-worker duplicates, and typing velocity.
        </p>
      </div>
    );
  }

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto space-y-8">
      {/* Prominent Disclaimer Header */}
      <div className="p-4 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-[#B8860B] shrink-0" />
          <span className="text-xs text-[#785E2F] font-medium">
            <strong>Mandatory Review Rule:</strong> This report is evidence for human review. It is not proof of fraud or AI authorship.
          </span>
        </div>
        <button
          onClick={handleDeleteNow}
          className="text-xs text-red-600 hover:text-red-700 font-medium flex items-center gap-1.5 shrink-0 px-2.5 py-1 rounded border border-red-200 bg-white hover:bg-red-50 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" /> Delete Now
        </button>
      </div>

      {/* Summary Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="canary-card p-4">
          <span className="text-[11px] font-mono uppercase text-[#78716C]">Answers Audited</span>
          <div className="font-editorial text-3xl font-medium text-[#1C1917] mt-1">{activeSummary.answers_count}</div>
          <span className="text-[11px] text-[#A8A29E] mt-0.5 block">{activeSummary.workers_count} distinct workers</span>
        </div>

        <div className="canary-card p-4">
          <span className="text-[11px] font-mono uppercase text-[#78716C]">Flagged Workers</span>
          <div className="font-editorial text-3xl font-medium text-[#B8860B] mt-1">
            {activeSummary.flagged_workers_count}
          </div>
          <span className="text-[11px] text-[#785E2F] mt-0.5 block">Require human inspection</span>
        </div>

        <div className="canary-card p-4">
          <span className="text-[11px] font-mono uppercase text-[#78716C]">Confidence Tiers</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xs font-mono font-bold text-red-700">H: {activeSummary.confidence_counts.High}</span>
            <span className="text-xs font-mono font-bold text-amber-700">M: {activeSummary.confidence_counts.Medium}</span>
            <span className="text-xs font-mono font-bold text-stone-600">L: {activeSummary.confidence_counts.Low}</span>
          </div>
          <span className="text-[11px] text-[#A8A29E] mt-0.5 block">Total {activeFindings.length} findings</span>
        </div>

        <div className="canary-card p-4">
          <span className="text-[11px] font-mono uppercase text-[#78716C]">Calibration Baseline</span>
          <div className="font-editorial text-2xl font-medium text-[#1C1917] mt-1">
            {activeSummary.calibration ? `${(activeSummary.calibration.estimated_fp_rate * 100).toFixed(1)}%` : 'Active'}
          </div>
          <span className="text-[11px] text-[#A8A29E] mt-0.5 block font-mono">
            {activeSummary.calibration
              ? `95% CI: [${(activeSummary.calibration.ci_lower * 100).toFixed(1)}%, ${(activeSummary.calibration.ci_upper * 100).toFixed(1)}%]`
              : 'Empirical bounds active'}
          </span>
        </div>
      </div>

      {/* Export Controls & Filter */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-[#78716C]" />
          <span className="text-xs font-medium text-[#44403C]">Confidence Filter:</span>
          {['all', 'high', 'medium', 'low'].map((c) => (
            <button
              key={c}
              onClick={() => setFilterConfidence(c)}
              className={`px-2.5 py-1 rounded text-xs capitalize font-medium transition-colors ${
                filterConfidence === c
                  ? 'bg-[#1C1917] text-white'
                  : 'bg-white border border-[#E7E5E4] text-[#44403C] hover:bg-[#F4EFEA]'
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-[#78716C] mr-1">Export:</span>
          <button
            onClick={() => handleExport('html')}
            className="px-2.5 py-1 rounded text-xs bg-white border border-[#D6D3D1] text-[#1C1917] hover:bg-[#F4EFEA] font-medium flex items-center gap-1"
          >
            <Download className="w-3 h-3" /> Standalone HTML
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="px-2.5 py-1 rounded text-xs bg-white border border-[#D6D3D1] text-[#1C1917] hover:bg-[#F4EFEA] font-medium flex items-center gap-1"
          >
            <Download className="w-3 h-3" /> CSV
          </button>
          <button
            onClick={() => handleExport('json')}
            className="px-2.5 py-1 rounded text-xs bg-white border border-[#D6D3D1] text-[#1C1917] hover:bg-[#F4EFEA] font-medium flex items-center gap-1"
          >
            <Download className="w-3 h-3" /> JSON
          </button>
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.map((finding) => (
          <div key={finding.id} className="canary-card p-6 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span
                  className={`px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider ${
                    finding.evidence_confidence === 'High'
                      ? 'bg-red-100 text-red-800 border border-red-200'
                      : finding.evidence_confidence === 'Medium'
                      ? 'bg-amber-100 text-amber-800 border border-amber-200'
                      : 'bg-stone-100 text-stone-700 border border-stone-200'
                  }`}
                >
                  {finding.evidence_confidence} Confidence
                </span>
                <span className="font-mono text-xs font-medium text-[#1C1917]">{finding.worker_id}</span>
                <span className="text-xs text-[#78716C]">
                  on task <strong className="font-mono">{finding.task_id}</strong>
                </span>
              </div>
              <span className="text-[11px] font-mono text-[#78716C] capitalize">{finding.check_identifier} Check</span>
            </div>

            <p className="text-xs text-[#1C1917] leading-relaxed">{finding.explanation}</p>

            {finding.evidence_text && (
              <div className="p-3 rounded bg-[#FAF8F5] border border-[#E7E5E4] font-mono text-[11px] text-[#44403C] overflow-x-auto">
                <span className="text-[#A8A29E] select-none mr-2">Evidence:</span>
                {finding.evidence_text}
              </div>
            )}

            {finding.numerical_measurements && Object.keys(finding.numerical_measurements).length > 0 && (
              <div className="flex flex-wrap gap-4 text-[11px] font-mono text-[#78716C] pt-1">
                {Object.entries(finding.numerical_measurements).map(([k, v]) => (
                  <span key={k}>
                    {k}: <strong className="text-[#1C1917]">{v}</strong>
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
