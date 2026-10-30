import React, { useEffect, useState } from 'react';
import { X, AlertTriangle, ArrowLeftRight, Loader2, Info } from 'lucide-react';
import { SideBySideComparisonResponse } from '../../types';

interface SideBySideComparisonModalProps {
  findingId: string | null;
  onClose: () => void;
}

export const SideBySideComparisonModal: React.FC<SideBySideComparisonModalProps> = ({
  findingId,
  onClose,
}) => {
  const [data, setData] = useState<SideBySideComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!findingId) return;
    const fetchComparison = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/v1/findings/${findingId}/comparison`);
        if (!res.ok) throw new Error('Failed to load text comparison.');
        const result: SideBySideComparisonResponse = await res.json();
        setData(result);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('An unexpected error occurred loading comparison.');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchComparison();
  }, [findingId]);

  if (!findingId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-[#1C1917]/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-2xl border border-[#E7E5E4] max-w-5xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#E7E5E4] bg-[#FAF8F5] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center border border-[#E8DEC8]">
              <ArrowLeftRight className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-editorial text-lg text-[#1C1917]">
                Side-by-Side Evidence Comparison
              </h3>
              <p className="text-xs font-mono text-[#78716C]">
                Task: {data?.task_id || '—'} | Worker: {data?.worker_id || '—'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {data?.similarity_score !== undefined && (
              <span className="px-2.5 py-1 rounded bg-[#B8860B]/10 text-[#B8860B] text-xs font-mono font-semibold border border-[#B8860B]/20">
                Similarity: {(data.similarity_score * 100).toFixed(1)}%
              </span>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-md text-[#78716C] hover:text-[#1C1917] hover:bg-[#E7E5E4] transition-colors"
              title="Close modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3 text-[#78716C]">
              <Loader2 className="w-8 h-8 animate-spin text-[#B8860B]" />
              <p className="text-xs font-mono">Aligning tokens and computing sequence diff...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-md bg-[#DC2626]/10 border border-[#DC2626]/20 text-[#DC2626] text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          ) : data ? (
            <>
              {/* Invariant & Methodology Banner */}
              <div className="p-3.5 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] flex items-start gap-2.5 text-xs text-[#78716C]">
                <Info className="w-4 h-4 text-[#B8860B] shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <span className="font-semibold text-[#1C1917]">Methodology & Limitation Notice:</span>
                  <p>{data.explanation}</p>
                  <p className="text-[11px] font-mono text-[#B8860B] font-medium">{data.limitations}</p>
                </div>
              </div>

              {/* Side-by-side split view */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Source worker answer */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between pb-1 border-b border-[#E7E5E4]">
                    <span className="text-xs font-mono uppercase tracking-wider text-[#1C1917] font-semibold">
                      Submitted Worker Answer
                    </span>
                    <span className="text-[10px] font-mono text-[#78716C]">
                      ID: {data.worker_id}
                    </span>
                  </div>
                  <div className="p-4 rounded-md border border-[#E7E5E4] bg-[#FCFBF9] text-xs leading-relaxed font-mono whitespace-pre-wrap min-h-[220px] max-h-[380px] overflow-y-auto">
                    {data.diff_segments.map((seg, idx) => {
                      if (seg.is_match) {
                        return (
                          <mark
                            key={idx}
                            className="bg-[#B8860B]/20 text-[#1C1917] font-semibold px-0.5 rounded"
                            title="Matching Text Segment"
                          >
                            {seg.text}
                          </mark>
                        );
                      }
                      if (seg.is_source_only) {
                        return (
                          <span key={idx} className="text-[#1C1917]">
                            {seg.text}
                          </span>
                        );
                      }
                      return null;
                    })}
                  </div>
                </div>

                {/* Target Comparison */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between pb-1 border-b border-[#E7E5E4]">
                    <span className="text-xs font-mono uppercase tracking-wider text-[#1C1917] font-semibold">
                      {data.target_label}
                    </span>
                    <span className="text-[10px] font-mono text-[#B8860B]">
                      {data.comparison_type}
                    </span>
                  </div>
                  <div className="p-4 rounded-md border border-[#E7E5E4] bg-[#FCFBF9] text-xs leading-relaxed font-mono whitespace-pre-wrap min-h-[220px] max-h-[380px] overflow-y-auto">
                    {data.diff_segments.map((seg, idx) => {
                      if (seg.is_match) {
                        return (
                          <mark
                            key={idx}
                            className="bg-[#B8860B]/20 text-[#1C1917] font-semibold px-0.5 rounded"
                            title="Matching Text Segment"
                          >
                            {seg.text}
                          </mark>
                        );
                      }
                      if (seg.is_target_only) {
                        return (
                          <span key={idx} className="text-[#78716C] italic opacity-85">
                            {seg.text}
                          </span>
                        );
                      }
                      return null;
                    })}
                  </div>
                </div>
              </div>

              {/* Numerical Measurements Drawer */}
              {Object.keys(data.measurements).length > 0 && (
                <div className="pt-2 border-t border-[#E7E5E4]">
                  <span className="text-xs font-mono uppercase tracking-wider text-[#78716C] font-semibold block mb-2">
                    Empirical Numerical Telemetry
                  </span>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    {Object.entries(data.measurements).map(([key, val]) => (
                      <div key={key} className="p-2.5 rounded bg-[#FAF8F5] border border-[#E7E5E4]">
                        <div className="text-[10px] font-mono uppercase text-[#78716C] truncate">{key.replace(/_/g, ' ')}</div>
                        <div className="text-sm font-mono font-medium text-[#1C1917] mt-0.5">
                          {typeof val === 'number' ? (val < 1 && val > 0 ? (val * 100).toFixed(2) + '%' : val) : String(val)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-[#E7E5E4] bg-[#FAF8F5] flex items-center justify-between">
          <div className="flex items-center gap-2 text-[11px] text-[#78716C]">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#B8860B]/30 border border-[#B8860B]"></span>
            <span>Highlighted segments denote common sequence substrings.</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
