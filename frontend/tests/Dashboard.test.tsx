import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { DashboardPage } from '../src/pages/DashboardPage';
import { DashboardStats, DashboardAuditsResponse } from '../src/types';

describe('Reviewer Dashboard Component (Milestone 1)', () => {
  const mockStats: DashboardStats = {
    total_audits: 12,
    completed_audits: 10,
    running_audits: 1,
    failed_audits: 1,
    total_answers_analyzed: 450,
    findings_requiring_review: 5,
    reviewed_findings: 18,
    high_confidence_findings: 3,
    medium_confidence_findings: 12,
    low_confidence_findings: 8,
    findings_by_category: {
      marker_detection: 12,
      similarity_reference: 6,
      worker_duplicate: 5,
    },
    audits_by_status: {
      completed: 10,
      running: 1,
      failed: 1,
    },
    activity_over_time: [
      { date: '2026-10-29', audits: 4, findings: 2 },
      { date: '2026-10-30', audits: 8, findings: 5 },
    ],
    dataset_size_distribution: {
      '1-50': 5,
      '51-200': 7,
      '201-1000': 0,
      '1000+': 0,
    },
  };

  const mockAudits: DashboardAuditsResponse = {
    total: 2,
    page: 1,
    page_size: 10,
    total_pages: 1,
    items: [
      {
        id: 'audit-001',
        dataset_name: 'test_dataset_a.json',
        status: 'completed',
        created_at: '2026-10-30T10:00:00Z',
        completed_at: '2026-10-30T10:02:30Z',
        duration_seconds: 150.0,
        answers_count: 100,
        workers_count: 20,
        flagged_workers_count: 3,
        findings_count: 3,
        expires_at: '2026-11-06T10:00:00Z',
        owner_id: 'reviewer_1',
      },
      {
        id: 'audit-002',
        dataset_name: 'batch_b.json',
        status: 'running',
        created_at: '2026-10-30T11:00:00Z',
        completed_at: undefined,
        duration_seconds: undefined,
        answers_count: 50,
        workers_count: 10,
        flagged_workers_count: 0,
        findings_count: 0,
        expires_at: '2026-11-06T11:00:00Z',
        owner_id: undefined,
      },
    ],
  };

  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/api/v1/dashboard/stats')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockStats),
          });
        }
        if (url.includes('/api/v1/dashboard/audits')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockAudits),
          });
        }
        return Promise.reject(new Error(`Unknown endpoint: ${url}`));
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders dashboard overview statistics and KPI cards', async () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Reviewer Workspace & Analytics/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText('12').length).toBeGreaterThan(0); // audits / findings
      expect(screen.getByText('450')).toBeInTheDocument(); // total answers
      expect(screen.getByText('test_dataset_a.json')).toBeInTheDocument();
      expect(screen.getByText('batch_b.json')).toBeInTheDocument();
    });
  });

  it('handles search input filter', async () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('test_dataset_a.json')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Search dataset name or ID/i);
    fireEvent.change(searchInput, { target: { value: 'batch_b' } });
    fireEvent.submit(searchInput.closest('form')!);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('search=batch_b')
      );
    });
  });

  it('renders empty state when no audits exist', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/api/v1/dashboard/stats')) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                ...mockStats,
                total_audits: 0,
                completed_audits: 0,
                running_audits: 0,
                failed_audits: 0,
                total_answers_analyzed: 0,
                activity_over_time: [],
              }),
          });
        }
        if (url.includes('/api/v1/dashboard/audits')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ total: 0, page: 1, page_size: 10, total_pages: 0, items: [] }),
          });
        }
        return Promise.reject(new Error(`Unknown endpoint: ${url}`));
      })
    );

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/No audit records found/i)).toBeInTheDocument();
      expect(screen.getByText(/Start New Audit/i)).toBeInTheDocument();
    });
  });
});
