import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { DatasetQualityView } from '../src/components/investigation/DatasetQualityView';
import { InvestigationPage } from '../src/pages/InvestigationPage';
import { DatasetQualityResponse, InvestigationWorkspaceResponse } from '../src/types';

describe('Dataset Quality Analytics (Milestone 3)', () => {
  const mockQuality: DatasetQualityResponse = {
    audit_id: 'audit-test-99',
    dataset_name: 'production_crowd_batch.csv',
    total_records: 120,
    unique_workers: 24,
    unique_tasks: 40,
    completeness_score: 94.5,
    empty_answers_count: 2,
    missing_worker_ids_count: 1,
    missing_timestamps_count: 5,
    duplicate_task_submissions_count: 8,
    duplicate_submissions_count: 3,
    length_stats: {
      min_chars: 14,
      max_chars: 1450,
      avg_chars: 285.4,
      median_chars: 210.0,
      min_words: 3,
      max_words: 240,
      avg_words: 48.2,
      median_words: 35.0,
      short_answers_count: 4,
      long_answers_count: 7,
    },
    length_distribution: [
      { bucket: '0-50', min_val: 0, max_val: 50, count: 8, percentage: 6.7 },
      { bucket: '51-150', min_val: 51, max_val: 150, count: 25, percentage: 20.8 },
      { bucket: '151-300', min_val: 151, max_val: 300, count: 50, percentage: 41.7 },
      { bucket: '301-600', min_val: 301, max_val: 600, count: 25, percentage: 20.8 },
      { bucket: '601-1200', min_val: 601, max_val: 1200, count: 8, percentage: 6.7 },
      { bucket: '1200+', min_val: 1201, count: 4, percentage: 3.3 },
    ],
    worker_participation: {
      min_answers: 1,
      max_answers: 28,
      avg_answers: 5.0,
      median_answers: 3.0,
      distribution_buckets: [
        { bucket: '1 answer', min_val: 1, max_val: 1, count: 6, percentage: 25.0 },
        { bucket: '2-5 answers', min_val: 2, max_val: 5, count: 12, percentage: 50.0 },
        { bucket: '6-10 answers', min_val: 6, max_val: 10, count: 4, percentage: 16.7 },
        { bucket: '11-20 answers', min_val: 11, max_val: 20, count: 1, percentage: 4.2 },
        { bucket: '20+ answers', min_val: 21, count: 1, percentage: 4.2 },
      ],
      top_contributors: [
        { worker_id: 'worker_heavy_lead', answer_count: 28, percentage_of_total: 23.3 },
        { worker_id: 'worker_runner_up', answer_count: 14, percentage_of_total: 11.7 },
      ],
    },
    task_coverage: {
      min_answers_per_task: 1,
      max_answers_per_task: 6,
      avg_answers_per_task: 3.0,
      coverage_buckets: [
        { bucket: '1 answer', min_val: 1, max_val: 1, count: 5, percentage: 12.5 },
        { bucket: '2-3 answers', min_val: 2, max_val: 3, count: 25, percentage: 62.5 },
        { bucket: '4-5 answers', min_val: 4, max_val: 5, count: 8, percentage: 20.0 },
        { bucket: '6-10 answers', min_val: 6, max_val: 10, count: 2, percentage: 5.0 },
        { bucket: '10+ answers', min_val: 11, count: 0, percentage: 0.0 },
      ],
    },
    submission_time_analysis: {
      timestamps_present_count: 115,
      timestamps_missing_count: 5,
      timestamp_coverage_pct: 95.8,
      hourly_distribution: {
        '00:00': 0,
        '01:00': 0,
        '08:00': 15,
        '09:00': 35,
        '10:00': 40,
        '11:00': 20,
        '12:00': 5,
      },
      avg_seconds_spent: 42.5,
      median_seconds_spent: 38.0,
    },
    warnings: [
      {
        code: 'EMPTY_ANSWERS',
        title: 'Empty or Blank Answers Detected',
        message: '2 records contain no answer text or only whitespace.',
        severity: 'warning',
        affected_records: 2,
      },
    ],
  };

  const mockWorkspace: InvestigationWorkspaceResponse = {
    audit: {
      id: 'audit-test-99',
      dataset_name: 'production_crowd_batch.csv',
      status: 'completed',
      answers_count: 120,
      workers_count: 24,
      flagged_workers_count: 0,
      consent_external_ai: false,
      created_at: '2026-10-30T10:00:00Z',
      completed_at: '2026-10-30T10:02:00Z',
      expires_at: '2026-11-06T10:00:00Z',
      summary_metrics: {},
    },
    findings: [],
    markers: [],
    duplicate_clusters: [],
  };

  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders dataset quality view with scorecard, warnings, histograms and stats', async () => {
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockQuality,
    });

    render(<DatasetQualityView auditId="audit-test-99" />);

    expect(
      screen.getByText(/computing dataset quality and hygiene profile/i)
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Dataset Quality & Hygiene Profile')).toBeInTheDocument();
    });

    // Scorecard
    expect(screen.getByText('94.5%')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('24')).toBeInTheDocument();
    expect(screen.getByText('40')).toBeInTheDocument();
    expect(screen.getByText('95.8%')).toBeInTheDocument();

    // Warnings
    expect(screen.getByText('Empty or Blank Answers Detected')).toBeInTheDocument();
    expect(screen.getByText('warning')).toBeInTheDocument();

    // Histograms
    expect(screen.getByText('0-50 chars')).toBeInTheDocument();
    expect(screen.getByText('151-300 chars')).toBeInTheDocument();
    expect(screen.getByText('worker_heavy_lead')).toBeInTheDocument();

    // Exports
    expect(screen.getByText('Export CSV')).toBeInTheDocument();
    expect(screen.getByText('Export JSON')).toBeInTheDocument();
  });

  it('supports switching to the Dataset Quality tab in InvestigationPage', async () => {
    (fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockWorkspace,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockQuality,
      });

    render(
      <MemoryRouter initialEntries={['/audits/audit-test-99']}>
        <Routes>
          <Route path="/audits/:auditId" element={<InvestigationPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Dataset Quality')).toBeInTheDocument();
    });

    // Click Dataset Quality tab
    fireEvent.click(screen.getByText('Dataset Quality'));

    await waitFor(() => {
      expect(screen.getByText('Dataset Quality & Hygiene Profile')).toBeInTheDocument();
      expect(screen.getByText('94.5%')).toBeInTheDocument();
    });
  });

  it('renders empty dataset hygiene state gracefully', async () => {
    const emptyQuality: DatasetQualityResponse = {
      ...mockQuality,
      total_records: 0,
      unique_workers: 0,
      unique_tasks: 0,
      completeness_score: 0.0,
      warnings: [
        {
          code: 'EMPTY_DATASET',
          title: 'Dataset Has Zero Records',
          message: 'No records found in this audit for quality profiling.',
          severity: 'warning',
          affected_records: 0,
        },
      ],
      length_distribution: [],
      worker_participation: {
        min_answers: 0,
        max_answers: 0,
        avg_answers: 0,
        median_answers: 0,
        distribution_buckets: [],
        top_contributors: [],
      },
      task_coverage: {
        min_answers_per_task: 0,
        max_answers_per_task: 0,
        avg_answers_per_task: 0,
        coverage_buckets: [],
      },
    };

    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => emptyQuality,
    });

    render(<DatasetQualityView auditId="audit-test-99" />);

    await waitFor(() => {
      expect(screen.getByText('0%')).toBeInTheDocument();
      expect(screen.getByText('Dataset Has Zero Records')).toBeInTheDocument();
    });
  });

  it('handles error states and retry button', async () => {
    (fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    render(<DatasetQualityView auditId="audit-test-99" />);

    await waitFor(() => {
      expect(screen.getByText('Quality Analytics Error')).toBeInTheDocument();
    });

    // Retry
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockQuality,
    });

    fireEvent.click(screen.getByText('Retry'));

    await waitFor(() => {
      expect(screen.getByText('Dataset Quality & Hygiene Profile')).toBeInTheDocument();
    });
  });
});
