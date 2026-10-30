import React, { useState } from 'react';
import { X, CheckCircle2, History, AlertCircle, ShieldAlert, Loader2 } from 'lucide-react';
import { FindingDetailedItem, ReviewStatus } from '../../types';

interface AdjudicationModalProps {
  finding: FindingDetailedItem | null;
  onClose: () => void;
  onUpdate: (updatedFinding: FindingDetailedItem) => void;
}

export const AdjudicationModal: React.FC<AdjudicationModalProps> = ({
  finding,
  onClose,
  onUpdate,
}) => {
  const [status, setStatus] = useState<ReviewStatus>(finding?.review_status || 'pending_review');
  const [notes, setNotes] = useState<string>(finding?.reviewer_notes || '');
  const [dismissalReason, setDismissalReason] = useState<string>('');
  const [assignedReviewer, setAssignedReviewer] = useState<string>(
    finding?.assigned_reviewer || ''
  );
  const [reviewerId, setReviewerId] = useState<string>('lead_reviewer');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!finding) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch(`/api/v1/findings/${finding.id}/review`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          review_status: status,
          reviewer_notes: notes.trim() || null,
          dismissal_reason: status === 'dismissed' ? dismissalReason.trim() : null,
          assigned_reviewer: assignedReviewer.trim() || null,
          reviewer_id: reviewerId.trim() || 'lead_reviewer',
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Failed to update review status.');
      }

      const updated: FindingDetailedItem = await res.json();
      onUpdate(updated);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred during adjudication.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#1C1917]/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-2xl border border-[#E7E5E4] max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#E7E5E4] bg-[#FAF8F5] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center border border-[#E8DEC8]">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-editorial text-lg text-[#1C1917]">Reviewer Adjudication & Notes</h3>
              <p className="text-xs font-mono text-[#78716C]">
                Finding: {finding.id.slice(0, 8)}... | Worker: {finding.worker_id}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-[#78716C] hover:text-[#1C1917] hover:bg-[#E7E5E4] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto flex-1 space-y-5">
          {error && (
            <div className="p-3 rounded-md bg-[#DC2626]/10 border border-[#DC2626]/20 text-[#DC2626] text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Invariant Warning */}
          <div className="p-3 rounded bg-[#FAF8F5] border border-[#E7E5E4] flex items-start gap-2.5 text-xs text-[#78716C]">
            <ShieldAlert className="w-4 h-4 text-[#B8860B] shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-[#1C1917]">Non-Automated Punishment Invariant:</span>
              <p className="text-[11px] mt-0.5">
                Human reviewer assessments serve as internal documentation for dataset stewards. Canary does
                not automatically reject submissions, penalize workers, or withhold payments.
              </p>
            </div>
          </div>

          {/* Status Selection */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase tracking-wider text-[#1C1917] font-semibold block">
              Adjudication Decision Status
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {(
                [
                  { value: 'pending_review', label: 'Pending Review' },
                  { value: 'under_review', label: 'Under Review' },
                  { value: 'reviewed', label: 'Confirmed / Reviewed' },
                  { value: 'dismissed', label: 'Dismissed (False Positive)' },
                  { value: 'needs_investigation', label: 'Needs Follow-Up' },
                ] as const
              ).map((option) => (
                <button
                  type="button"
                  key={option.value}
                  onClick={() => setStatus(option.value)}
                  className={`p-2.5 rounded text-xs text-left border transition-all ${
                    status === option.value
                      ? 'border-[#1C1917] bg-[#1C1917] text-[#FAF8F5] font-medium shadow-sm'
                      : 'border-[#E7E5E4] bg-white text-[#44403C] hover:bg-[#FAF8F5]'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Dismissal Reason if dismissed */}
          {status === 'dismissed' && (
            <div className="space-y-1.5 animate-in fade-in duration-150">
              <label className="text-xs font-mono uppercase tracking-wider text-[#DC2626] font-semibold block">
                Reason for Dismissal *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Common public quotation; expected domain jargon; benign boilerplate"
                value={dismissalReason}
                onChange={(e) => setDismissalReason(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded border border-[#DC2626]/40 focus:outline-none focus:ring-1 focus:ring-[#DC2626]"
              />
            </div>
          )}

          {/* Reviewer Assignment & Identity */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-mono uppercase tracking-wider text-[#78716C] block">
                Assign Reviewer
              </label>
              <input
                type="text"
                placeholder="e.g. sarah_auditor"
                value={assignedReviewer}
                onChange={(e) => setAssignedReviewer(e.target.value)}
                className="w-full px-3 py-1.5 text-xs rounded border border-[#D6D3D1] focus:outline-none focus:ring-1 focus:ring-[#1C1917]"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-mono uppercase tracking-wider text-[#78716C] block">
                Your Reviewer Identifier
              </label>
              <input
                type="text"
                value={reviewerId}
                onChange={(e) => setReviewerId(e.target.value)}
                className="w-full px-3 py-1.5 text-xs rounded border border-[#D6D3D1] focus:outline-none focus:ring-1 focus:ring-[#1C1917]"
              />
            </div>
          </div>

          {/* Reviewer Notes */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase tracking-wider text-[#78716C] block">
              Investigator Notes & Rationale
            </label>
            <textarea
              rows={4}
              placeholder="Record contextual evidence, worker task patterns, or reasons why this finding requires stewardship intervention..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full p-3 text-xs rounded border border-[#D6D3D1] focus:outline-none focus:ring-1 focus:ring-[#1C1917] font-mono leading-relaxed"
            />
          </div>

          {/* Historical Review Audit Trail */}
          {finding.history && finding.history.length > 0 && (
            <div className="space-y-2 pt-2 border-t border-[#E7E5E4]">
              <div className="flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider text-[#78716C]">
                <History className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>Decision Audit Trail ({finding.history.length})</span>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                {finding.history.map((item) => (
                  <div key={item.id} className="p-2.5 rounded bg-[#FAF8F5] border border-[#E7E5E4] text-xs space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-mono text-[#78716C]">
                      <span className="font-semibold text-[#1C1917]">{item.reviewer_id}</span>
                      <span>{new Date(item.created_at).toLocaleString()}</span>
                    </div>
                    <div className="text-[11px]">
                      Status changed: <span className="font-mono text-[#78716C]">{item.previous_status}</span> &rarr;{' '}
                      <span className="font-mono font-medium text-[#1C1917]">{item.new_status}</span>
                    </div>
                    {item.notes && <p className="text-[11px] font-mono text-[#44403C] mt-1 bg-white p-1.5 rounded border border-[#E7E5E4]">{item.notes}</p>}
                    {item.dismissal_reason && (
                      <p className="text-[11px] font-mono text-[#DC2626] bg-[#DC2626]/5 p-1 rounded">
                        Dismissal: {item.dismissal_reason}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-[#E7E5E4]">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2 rounded border border-[#D6D3D1] text-xs font-medium text-[#44403C] hover:bg-[#FAF8F5] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors flex items-center gap-1.5 shadow-sm disabled:opacity-50"
            >
              {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              Save Adjudication
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
