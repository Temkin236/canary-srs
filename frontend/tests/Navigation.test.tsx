import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { App } from '../src/App';

describe('Website Navigation (FR-46)', () => {
  it('renders How It Works page at /how-it-works', () => {
    render(
      <MemoryRouter initialEntries={['/how-it-works']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /How Canary Audits Human Datasets/i })).toBeInTheDocument();
    expect(screen.getByText(/Task Preparation & Marker Seeding/i)).toBeInTheDocument();
  });

  it('renders Prepare Tasks page at /prepare', () => {
    render(
      <MemoryRouter initialEntries={['/prepare']}>
        <App />
      </MemoryRouter>
    );
    expect(
      screen.getByRole('heading', { name: /Task Preparation & Marker Generation/i })
    ).toBeInTheDocument();
  });

  it('renders Start Audit page at /audit', () => {
    render(
      <MemoryRouter initialEntries={['/audit']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Upload Dataset & Run Audit/i })).toBeInTheDocument();
  });

  it('renders Accuracy & Evaluation page at /accuracy', () => {
    render(
      <MemoryRouter initialEntries={['/accuracy']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Measured Accuracy & Evaluation/i })).toBeInTheDocument();
  });

  it('renders Reviewer Dashboard page at /dashboard', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Reviewer Workspace & Analytics/i })).toBeInTheDocument();
  });

  it('renders Privacy Policy page at /privacy', () => {
    render(
      <MemoryRouter initialEntries={['/privacy']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Privacy & Data Retention Policy/i })).toBeInTheDocument();
    expect(screen.getAllByText(/7-Day Ephemeral Retention/i).length).toBeGreaterThan(0);
  });

  it('renders Responsible-Use Terms page at /terms', () => {
    render(
      <MemoryRouter initialEntries={['/terms']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Responsible-Use Terms/i })).toBeInTheDocument();
    expect(screen.getByText(/No Automated Penalties/i)).toBeInTheDocument();
  });

  it('renders Contact page at /contact', () => {
    render(
      <MemoryRouter initialEntries={['/contact']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /Contact & Feedback/i })).toBeInTheDocument();
  });
});
