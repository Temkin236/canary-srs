import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { InvestigationPage } from '../src/pages/InvestigationPage';
import { InvestigationWorkspaceResponse, SideBySideComparisonResponse } from '../src/types';

describe('Investigation Workspace & Reviewer Adjudication (Milestone 2)', () => {
  const mockWorkspace: InvestigationWorkspaceResponse = {
    audit: {
      id: 'audit-test-99',
      dataset_name: 'production_crowd_batch.csv',
      status: 'completed',
      answers_count: 50,
      workers_count: 15,
      flagged_workers_count: 3,
      consent_external_ai: false,
      created_at: '2026-10-30T10:00:00Z',
      completed_at: '2026-10-30T10:02:00Z',
      expires_at: '2026-11-06T10:00:00Z',
      summary_metrics: { clean_answers_count: 47 },
    },
    findings: [
      {
        id: 'fnd-101',
        audit_id: 'audit-test-99',
        answer_id: 'ans-101',
        task_id: 'task-gen-01',
        worker_id: 'worker-alpha',
        check_identifier: 'marker',
        finding_type: 'exact_marker_echo',
        evidence_confidence: 'High',
        explanation: 'Worker echoed canary marker token in submission.',
        evidence_text: 'The solution is [cnry_test_marker] followed by proof.',
        numerical_measurements: { edit_distance: 0 },
        related_answer_ids: [],
        limitations: 'Evidence for human review only; does not prove cheating.',
        review_status: 'pending_review',
        created_at: '2026-10-30T10:01:00Z',
        history: [],
      },
      {
        id: 'fnd-102',
        audit_id: 'audit-test-99',
        answer_id: 'ans-102',
        task_id: 'task-gen-02',
        worker_id: 'worker-beta',
        check_identifier: 'similarity',
        finding_type: 'model_reference_top_percentile',
        evidence_confidence: 'Medium',
        explanation: 'Lexical similarity matches model reference output.',
        evidence_text: 'Relational database query optimization techniques...',
        numerical_measurements: { similarity: 0.92 },
        related_answer_ids: [],
        limitations: 'Evidence for human review only; does not prove cheating.',
        review_status: 'under_review',
        assigned_reviewer: 'sarah_reviewer',
        created_at: '2026-10-30T10:01:30Z',
        history: [
          {
            id: 'hist-1',
            finding_id: 'fnd-102',
            action: 'status_change',
            previous_status: 'pending_review',
            new_status: 'under_review',
            reviewer_id: 'sarah_reviewer',
            notes: 'Investigating peer distribution on task 2.',
            created_at: '2026-10-30T10:05:00Z',
          },
        ],
      },
    ],
    markers: [
      {
        id: 'm-1',
        task_id: 'task-gen-01',
        marker_id: 'm-1',
        expected_marker: 'cnry_test_marker',
        detected: true,
        detected_marker: 'cnry_test_marker',
        location_in_answer: [16, 34],
        preparation_version: 'v1.0',
        finding_id: 'fnd-101',
      },
    ],
    duplicate_clusters: [
      {
        cluster_id: 'cluster_001',
        task_id: 'task-gen-03',
        worker_ids: ['worker-gamma', 'worker-delta'],
        answer_ids: ['ans-103', 'ans-104'],
        representative_text: 'Duplicate submission sample text.',
        similarity_matrix: { 'worker-delta': 0.98 },
        findings_count: 2,
      },
    ],
    calibration: {
      sample_size: 50,
      flagged_count: 2,
      estimated_fp_rate: 0.04,
      ci_lower: 0.011,
      ci_upper: 0.134,
      ci_method: 'wilson',
    },
  };

  const mockComparison: SideBySideComparisonResponse = {
    finding_id: 'fnd-101',
    task_id: 'task-gen-01',
    worker_id: 'worker-alpha',
    comparison_type: 'marker_verification',
    source_answer: 'The solution is cnry_test_marker followed by proof.',
    target_answer: 'cnry_test_marker',
    target_label: 'Expected Canary Marker',
    similarity_score: 1.0,
    measurements: { edit_distance: 0 },
    explanation: 'Worker echoed canary marker.',
    diff_segments: [
      { text: 'The solution is ', is_match: false, is_source_only: true, is_target_only: false },
      { text: 'cnry_test_marker', is_match: true, is_source_only: false, is_target_only: false },
      { text: ' followed by proof.', is_match: false, is_source_only: true, is_target_only: false },
    ],
    limitations: 'Evidence for human review only; does not prove AI authorship, fraud, or cheating.',
  };

  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/api/v1/audits/audit-test-99/investigate')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockWorkspace),
          });
        }
        if (url.includes('/api/v1/findings/fnd-101/comparison')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockComparison),
          });
        }
        if (url.includes('/api/v1/findings/fnd-101/review')) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                ...mockWorkspace.findings[0],
                review_status: 'reviewed',
                reviewer_notes: 'Verified marker echo.',
              }),
          });
        }
        return Promise.reject(new Error(`Unknown endpoint: ${url}`));
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders investigation workspace and findings table', async () => {
    render(
      <MemoryRouter initialEntries={['/audits/audit-test-99']}>
        <Routes>
          <Route path="/audits/:auditId" element={<InvestigationPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Evidence Adjudication Workspace/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/worker-alpha/i)).toBeInTheDocument();
      expect(screen.getByText(/worker-beta/i)).toBeInTheDocument();
      expect(screen.getAllByText(/pending review/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/under review/i).length).toBeGreaterThan(0);
    });
  });

  it('switches between investigation tabs (Overview, Markers, Duplicates, Review History)', async () => {
    render(
      <MemoryRouter initialEntries={['/audits/audit-test-99']}>
        <Routes>
          <Route path="/audits/:auditId" element={<InvestigationPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/worker-alpha/i)).toBeInTheDocument();
    });

    // Switch to Overview tab
    fireEvent.click(screen.getByRole('button', { name: /Overview & Metadata/i }));
    await waitFor(() => {
      expect(screen.getByText(/Statistical Calibration & Wilson CI/i)).toBeInTheDocument();
      expect(screen.getByText('4.00%')).toBeInTheDocument(); // estimated FP rate
    });

    // Switch to Marker Verification tab
    fireEvent.click(screen.getByRole('button', { name: /Marker Verification/i }));
    await waitFor(() => {
      expect(screen.getByText('cnry_test_marker')).toBeInTheDocument();
      expect(screen.getByText('Echoed in Answer')).toBeInTheDocument();
    });

    // Switch to Duplicate Clusters tab
    fireEvent.click(screen.getByRole('button', { name: /Duplicate Clusters/i }));
    await waitFor(() => {
      expect(screen.getByText('cluster_001')).toBeInTheDocument();
      expect(screen.getByText(/worker-gamma, worker-delta/i)).toBeInTheDocument();
    });

    // Switch to Review History tab
    fireEvent.click(screen.getByRole('button', { name: /Review History/i }));
    await waitFor(() => {
      expect(screen.getByText(/Stewardship Adjudication Trail/i)).toBeInTheDocument();
      expect(screen.getByText(/Investigating peer distribution on task 2/i)).toBeInTheDocument();
    });
  });

  it('opens side-by-side comparison modal', async () => {
    render(
      <MemoryRouter initialEntries={['/audits/audit-test-99']}>
        <Routes>
          <Route path="/audits/:auditId" element={<InvestigationPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/worker-alpha/i)).toBeInTheDocument();
    });

    const compareButtons = screen.getAllByRole('button', { name: /Compare/i });
    fireEvent.click(compareButtons[0]);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Side-by-Side Evidence Comparison/i })).toBeInTheDocument();
      expect(screen.getByText('Expected Canary Marker')).toBeInTheDocument();
      expect(screen.getByText('Similarity: 100.0%')).toBeInTheDocument();
    });

    // Close comparison modal
    fireEvent.click(screen.getByRole('button', { name: /Done/i }));
    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /Side-by-Side Evidence Comparison/i })).not.toBeInTheDocument();
    });
  });

  it('opens adjudication modal and updates finding status', async () => {
    render(
      <MemoryRouter initialEntries={['/audits/audit-test-99']}>
        <Routes>
          <Route path="/audits/:auditId" element={<InvestigationPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/worker-alpha/i)).toBeInTheDocument();
    });

    const adjudicateButtons = screen.getAllByRole('button', { name: /Adjudicate/i });
    fireEvent.click(adjudicateButtons[0]);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Reviewer Adjudication & Notes/i })).toBeInTheDocument();
    });

    // Click 'Confirmed / Reviewed' status button
    fireEvent.click(screen.getByRole('button', { name: /Confirmed \/ Reviewed/i }));

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Save Adjudication/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/findings/fnd-101/review',
        expect.objectContaining({
          method: 'PATCH',
        })
      );
    });
  });
});
