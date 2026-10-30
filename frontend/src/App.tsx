import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { DashboardPage } from './pages/DashboardPage';
import { HowItWorksPage } from './pages/HowItWorksPage';
import { PreparePage } from './pages/PreparePage';
import { AuditPage } from './pages/AuditPage';
import { ResultsPage } from './pages/ResultsPage';
import { AccuracyPage } from './pages/AccuracyPage';
import { PrivacyPage } from './pages/PrivacyPage';
import { TermsPage } from './pages/TermsPage';
import { ContactPage } from './pages/ContactPage';
import { NotFoundPage } from './pages/NotFoundPage';

export const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="how-it-works" element={<HowItWorksPage />} />
        <Route path="prepare" element={<PreparePage />} />
        <Route path="audit" element={<AuditPage />} />
        <Route path="results/:secret" element={<ResultsPage />} />
        <Route path="accuracy" element={<AccuracyPage />} />
        <Route path="privacy" element={<PrivacyPage />} />
        <Route path="terms" element={<TermsPage />} />
        <Route path="contact" element={<ContactPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};
