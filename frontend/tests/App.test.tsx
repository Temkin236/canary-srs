import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { App } from '../src/App';

describe('Canary SRS Frontend', () => {
  it('renders the homepage with authoritative mission statement', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    // Headline verification
    expect(
      screen.getByText(/Canary finds evidence that human-written dataset answers may have been contaminated by chatbot output/i)
    ).toBeInTheDocument();

    // Invariant statement
    expect(screen.getByText(/Evidence, Not Proof/i)).toBeInTheDocument();

    // Core CTAs
    expect(screen.getByRole('link', { name: /Start an Audit/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Prepare Tasks with Markers/i })).toBeInTheDocument();
  });
});
