import React, { useEffect, useState } from 'react';
import {
  Download,
  AlertTriangle,
  CheckCircle2,
  Users,
  FileText,
  Clock,
  Layers,
  BarChart2,
  Loader2,
  Info,
  AlertCircle,
} from 'lucide-react';
import { DatasetQualityResponse } from '../../types';

interface DatasetQualityViewProps {
  auditId: string;
}

export const DatasetQualityView: React.FC<DatasetQualityViewProps> = ({ auditId }) => {
  const [quality, setQuality] = useState<DatasetQualityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQuality = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/audits/${auditId}/quality`);
      if (!res.ok) {
        throw new Error('Failed to load dataset quality analytics.');
      }
      const json: DatasetQualityResponse = await res.json();
      setQuality(json);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred while loading quality profile.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuality();
  }, [auditId]);

  const handleExport = (format: 'csv' | 'json') => {
    const url = `/api/v1/audits/${auditId}/quality/export?format=${format}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `canary_quality_${auditId.slice(0, 8)}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-3 text-[#78716C]">
        <Loader2 className="w-8 h-8 animate-spin mx-auto text-[#B8860B]" />
        <p className="text-xs font-mono">Computing dataset quality and hygiene profile...</p>
      </div>
    );
  }

  if (error || !quality) {
    return (
      <div className="p-6 rounded-lg bg-[#DC2626]/10 border border-[#DC2626]/20 text-[#DC2626] text-xs space-y-3 max-w-lg mx-auto">
        <div className="flex items-center gap-2 font-semibold">
          <AlertTriangle className="w-4 h-4" />
          <span>Quality Analytics Error</span>
        </div>
        <p>{error || 'Dataset quality profile could not be retrieved.'}</p>
        <button
          onClick={fetchQuality}
          className="px-3 py-1.5 rounded bg-[#DC2626] text-white text-xs font-medium hover:bg-[#B91C1C] transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  const scoreColor =
    quality.completeness_score >= 90
      ? 'text-[#10B981]'
      : quality.completeness_score >= 70
        ? 'text-[#B8860B]'
        : 'text-[#DC2626]';

  const scoreBarColor =
    quality.completeness_score >= 90
      ? 'bg-[#10B981]'
      : quality.completeness_score >= 70
        ? 'bg-[#B8860B]'
        : 'bg-[#DC2626]';

  const maxHourlyCount = Math.max(
    1,
    ...Object.values(quality.submission_time_analysis.hourly_distribution)
  );

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="p-5 rounded-lg bg-white border border-[#E7E5E4] flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h2 className="font-editorial text-xl text-[#1C1917]">
              Dataset Quality &amp; Hygiene Profile
            </h2>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#E7E5E4] text-[#44403C]">
              {quality.dataset_name}
            </span>
          </div>
          <p className="text-xs text-[#78716C] max-w-2xl">
            Descriptive hygiene metrics evaluating dataset completeness, participation distribution,
            and formatting integrity.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-[#D6D3D1] bg-white text-xs font-medium text-[#1C1917] hover:bg-[#F5F5F4] transition-colors"
            title="Download formatted CSV report with formula injection mitigation"
          >
            <Download className="w-3.5 h-3.5 text-[#78716C]" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => handleExport('json')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-[#D6D3D1] bg-white text-xs font-medium text-[#1C1917] hover:bg-[#F5F5F4] transition-colors"
            title="Download full JSON dataset profile"
          >
            <Download className="w-3.5 h-3.5 text-[#78716C]" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Philosophical Invariant Callout */}
      <div className="p-3.5 rounded-lg bg-[#FAF8F5] border border-[#E7E5E4] flex items-start gap-2.5 text-xs text-[#57534E]">
        <Info className="w-4 h-4 text-[#B8860B] shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-[#1C1917]">
            Core Invariant (Evidence, Not Verdict):
          </span>{' '}
          Dataset hygiene analytics are descriptive metrics for dataset curators. They identify
          missing fields, submission velocity, and participation patterns, but{' '}
          <strong>never constitute evidence of AI authorship, fraud, or worker cheating</strong>.
        </div>
      </div>

      {/* Scorecard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Completeness Score */}
        <div className="p-4 rounded-lg bg-white border border-[#E7E5E4] space-y-2">
          <div className="text-[11px] font-mono uppercase tracking-wider text-[#78716C]">
            Completeness Score
          </div>
          <div className={`text-2xl font-editorial font-bold ${scoreColor}`}>
            {quality.completeness_score}%
          </div>
          <div className="w-full h-1.5 rounded-full bg-[#E7E5E4] overflow-hidden">
            <div
              className={`h-full ${scoreBarColor} transition-all duration-500`}
              style={{ width: `${Math.min(100, Math.max(0, quality.completeness_score))}%` }}
            />
          </div>
          <div className="text-[10px] text-[#78716C]">
            Weighted by non-empty, worker ID, task ID, and timestamps
          </div>
        </div>

        {/* Total Records */}
        <div className="p-4 rounded-lg bg-white border border-[#E7E5E4] space-y-1">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#78716C]">
            <span>Total Records</span>
            <FileText className="w-3.5 h-3.5" />
          </div>
          <div className="text-2xl font-editorial font-bold text-[#1C1917]">
            {quality.total_records.toLocaleString()}
          </div>
          <div className="text-[10px] text-[#78716C]">
            {quality.empty_answers_count} empty / blank answers
          </div>
        </div>

        {/* Unique Workers */}
        <div className="p-4 rounded-lg bg-white border border-[#E7E5E4] space-y-1">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#78716C]">
            <span>Unique Workers</span>
            <Users className="w-3.5 h-3.5" />
          </div>
          <div className="text-2xl font-editorial font-bold text-[#1C1917]">
            {quality.unique_workers.toLocaleString()}
          </div>
          <div className="text-[10px] text-[#78716C]">
            {quality.missing_worker_ids_count} records missing worker ID
          </div>
        </div>

        {/* Unique Tasks */}
        <div className="p-4 rounded-lg bg-white border border-[#E7E5E4] space-y-1">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#78716C]">
            <span>Unique Tasks</span>
            <Layers className="w-3.5 h-3.5" />
          </div>
          <div className="text-2xl font-editorial font-bold text-[#1C1917]">
            {quality.unique_tasks.toLocaleString()}
          </div>
          <div className="text-[10px] text-[#78716C]">
            {quality.duplicate_task_submissions_count} duplicate task entries
          </div>
        </div>

        {/* Timestamps */}
        <div className="p-4 rounded-lg bg-white border border-[#E7E5E4] space-y-1">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#78716C]">
            <span>Timestamp Coverage</span>
            <Clock className="w-3.5 h-3.5" />
          </div>
          <div className="text-2xl font-editorial font-bold text-[#1C1917]">
            {quality.submission_time_analysis.timestamp_coverage_pct}%
          </div>
          <div className="text-[10px] text-[#78716C]">
            {quality.missing_timestamps_count} missing timestamps
          </div>
        </div>
      </div>

      {/* Quality Warnings Section */}
      <div className="p-5 rounded-lg bg-white border border-[#E7E5E4] space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-[#78716C]" />
            <h3 className="font-editorial text-sm text-[#1C1917] font-semibold">
              Data Quality Warnings &amp; Hygiene Alerts
            </h3>
          </div>
          <span className="text-xs font-mono text-[#78716C]">
            {quality.warnings.length} {quality.warnings.length === 1 ? 'warning' : 'warnings'}
          </span>
        </div>

        {quality.warnings.length === 0 ? (
          <div className="p-4 rounded-lg bg-[#10B981]/5 border border-[#10B981]/20 flex items-center gap-2 text-xs text-[#10B981]">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>No data quality anomalies detected. The dataset exhibits clean hygiene.</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {quality.warnings.map((w, idx) => {
              const badgeStyle =
                w.severity === 'critical'
                  ? 'bg-[#DC2626]/10 text-[#DC2626] border-[#DC2626]/20'
                  : w.severity === 'warning'
                    ? 'bg-[#B8860B]/10 text-[#B8860B] border-[#B8860B]/20'
                    : 'bg-[#0284C7]/10 text-[#0284C7] border-[#0284C7]/20';

              return (
                <div
                  key={`${w.code}-${idx}`}
                  className="p-3.5 rounded border border-[#E7E5E4] bg-[#FAF8F5] space-y-1.5"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs font-semibold text-[#1C1917]">
                      {w.title}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${badgeStyle}`}
                    >
                      {w.severity}
                    </span>
                  </div>
                  <p className="text-xs text-[#57534E]">{w.message}</p>
                  <div className="text-[11px] font-mono text-[#78716C]">
                    Affected records: {w.affected_records}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Answer Length Distribution & Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Answer Length Histogram */}
        <div className="p-5 rounded-lg bg-white border border-[#E7E5E4] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-editorial text-sm text-[#1C1917] font-semibold">
                Answer Length Distribution
              </h3>
              <p className="text-[11px] text-[#78716C]">Character length bucketed distribution</p>
            </div>
            <BarChart2 className="w-4 h-4 text-[#78716C]" />
          </div>

          <div className="space-y-2.5">
            {quality.length_distribution.map((bucket) => (
              <div key={bucket.bucket} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-[#44403C]">{bucket.bucket} chars</span>
                  <span className="text-[#78716C]">
                    {bucket.count} ({bucket.percentage}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded bg-[#E7E5E4] overflow-hidden">
                  <div
                    className="h-full bg-[#1C1917] transition-all duration-300"
                    style={{ width: `${bucket.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Quick Length Stats Table */}
          <div className="pt-3 border-t border-[#E7E5E4] grid grid-cols-4 gap-2 text-center text-xs font-mono">
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">MIN CHARS</div>
              <div className="font-semibold text-[#1C1917]">{quality.length_stats.min_chars}</div>
            </div>
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">AVG CHARS</div>
              <div className="font-semibold text-[#1C1917]">{quality.length_stats.avg_chars}</div>
            </div>
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">MEDIAN CHARS</div>
              <div className="font-semibold text-[#1C1917]">
                {quality.length_stats.median_chars}
              </div>
            </div>
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">MAX CHARS</div>
              <div className="font-semibold text-[#1C1917]">{quality.length_stats.max_chars}</div>
            </div>
          </div>
        </div>

        {/* Worker Participation & Concentration */}
        <div className="p-5 rounded-lg bg-white border border-[#E7E5E4] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-editorial text-sm text-[#1C1917] font-semibold">
                Worker Participation Distribution
              </h3>
              <p className="text-[11px] text-[#78716C]">
                Submissions per individual worker contributor
              </p>
            </div>
            <Users className="w-4 h-4 text-[#78716C]" />
          </div>

          <div className="space-y-2.5">
            {quality.worker_participation.distribution_buckets.map((wb) => (
              <div key={wb.bucket} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-[#44403C]">{wb.bucket}</span>
                  <span className="text-[#78716C]">
                    {wb.count} workers ({wb.percentage}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded bg-[#E7E5E4] overflow-hidden">
                  <div
                    className="h-full bg-[#B8860B] transition-all duration-300"
                    style={{ width: `${wb.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Top Contributors Table */}
          <div className="pt-3 border-t border-[#E7E5E4] space-y-2">
            <div className="text-xs font-semibold text-[#1C1917]">Top Contributors</div>
            {quality.worker_participation.top_contributors.length === 0 ? (
              <div className="text-xs text-[#78716C] italic">No worker records recorded.</div>
            ) : (
              <div className="overflow-x-auto max-h-44">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="text-[10px] text-[#78716C] uppercase border-b border-[#E7E5E4]">
                    <tr>
                      <th className="pb-1">Worker</th>
                      <th className="pb-1 text-right">Answers</th>
                      <th className="pb-1 text-right">% of Dataset</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E7E5E4]">
                    {quality.worker_participation.top_contributors.map((tc) => (
                      <tr key={tc.worker_id} className="hover:bg-[#FAF8F5]">
                        <td className="py-1 text-[#1C1917] font-medium">{tc.worker_id}</td>
                        <td className="py-1 text-right text-[#57534E]">{tc.answer_count}</td>
                        <td className="py-1 text-right">
                          <span
                            className={
                              tc.percentage_of_total > 35
                                ? 'text-[#DC2626] font-semibold'
                                : 'text-[#78716C]'
                            }
                          >
                            {tc.percentage_of_total}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Task Coverage & Submission-Time Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Task Coverage Distribution */}
        <div className="p-5 rounded-lg bg-white border border-[#E7E5E4] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-editorial text-sm text-[#1C1917] font-semibold">
                Task Coverage Distribution
              </h3>
              <p className="text-[11px] text-[#78716C]">Answers recorded per distinct task prompt</p>
            </div>
            <Layers className="w-4 h-4 text-[#78716C]" />
          </div>

          <div className="space-y-2.5">
            {quality.task_coverage.coverage_buckets.map((tb) => (
              <div key={tb.bucket} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-[#44403C]">{tb.bucket}</span>
                  <span className="text-[#78716C]">
                    {tb.count} tasks ({tb.percentage}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded bg-[#E7E5E4] overflow-hidden">
                  <div
                    className="h-full bg-[#10B981] transition-all duration-300"
                    style={{ width: `${tb.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-[#E7E5E4] grid grid-cols-3 gap-2 text-center text-xs font-mono">
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">MIN / TASK</div>
              <div className="font-semibold text-[#1C1917]">
                {quality.task_coverage.min_answers_per_task}
              </div>
            </div>
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">AVG / TASK</div>
              <div className="font-semibold text-[#1C1917]">
                {quality.task_coverage.avg_answers_per_task}
              </div>
            </div>
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">MAX / TASK</div>
              <div className="font-semibold text-[#1C1917]">
                {quality.task_coverage.max_answers_per_task}
              </div>
            </div>
          </div>
        </div>

        {/* 24-Hour Submission-Time Histogram */}
        <div className="p-5 rounded-lg bg-white border border-[#E7E5E4] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-editorial text-sm text-[#1C1917] font-semibold">
                Submission-Time 24-Hour Profile
              </h3>
              <p className="text-[11px] text-[#78716C]">UTC hourly distribution of submissions</p>
            </div>
            <Clock className="w-4 h-4 text-[#78716C]" />
          </div>

          {/* 24 hour bar chart */}
          <div className="pt-6 h-32 flex items-end justify-between gap-1 border-b border-[#E7E5E4]">
            {Object.entries(quality.submission_time_analysis.hourly_distribution).map(
              ([hour, count]) => {
                const heightPct = count > 0 ? Math.round((count / maxHourlyCount) * 100) : 4;
                return (
                  <div
                    key={hour}
                    className="flex-1 flex flex-col items-center group relative cursor-pointer"
                  >
                    <div
                      className={`w-full rounded-t transition-all ${
                        count > 0 ? 'bg-[#1C1917] group-hover:bg-[#B8860B]' : 'bg-[#E7E5E4]'
                      }`}
                      style={{ height: `${heightPct}%` }}
                    />
                    {/* Tooltip */}
                    <div className="absolute -top-7 hidden group-hover:block bg-[#1C1917] text-white text-[9px] font-mono px-1.5 py-0.5 rounded shadow z-10 whitespace-nowrap">
                      {hour}: {count}
                    </div>
                  </div>
                );
              }
            )}
          </div>
          <div className="flex justify-between text-[10px] font-mono text-[#78716C]">
            <span>00:00</span>
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
            <span>23:00</span>
          </div>

          <div className="pt-2 grid grid-cols-2 gap-2 text-center text-xs font-mono">
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">AVG SECONDS SPENT</div>
              <div className="font-semibold text-[#1C1917]">
                {quality.submission_time_analysis.avg_seconds_spent !== null &&
                quality.submission_time_analysis.avg_seconds_spent !== undefined
                  ? `${quality.submission_time_analysis.avg_seconds_spent}s`
                  : 'N/A'}
              </div>
            </div>
            <div className="p-2 rounded bg-[#FAF8F5]">
              <div className="text-[10px] text-[#78716C]">MEDIAN SECONDS SPENT</div>
              <div className="font-semibold text-[#1C1917]">
                {quality.submission_time_analysis.median_seconds_spent !== null &&
                quality.submission_time_analysis.median_seconds_spent !== undefined
                  ? `${quality.submission_time_analysis.median_seconds_spent}s`
                  : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
