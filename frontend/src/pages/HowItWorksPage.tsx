import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, Database, Shield, Cpu, FileOutput } from 'lucide-react';

export const HowItWorksPage: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: 'Task Preparation & Marker Seeding',
      icon: Shield,
      desc: 'Before distributing tasks to workers or crowd vendors, generate cryptographically random canary markers. Seed these markers into prompt templates using zero-width Unicode sequences or subtle instruction prompts. Export the manifest.',
    },
    {
      num: '02',
      title: 'Dataset Ingestion & Validation',
      icon: Database,
      desc: 'When completed worker submissions arrive, upload the CSV or JSONL dataset. Canary rigorously checks encoding, validates required columns (task_id, prompt, worker_id, answer), and reports row-level errors prior to execution.',
    },
    {
      num: '03',
      title: 'Multi-Modal Detection Pipeline',
      icon: Cpu,
      desc: 'Canary runs four checks: (1) exact and typo-bounded marker detection; (2) AI reference output similarity contextualized by peer distributions; (3) cross-worker duplicate clustering; and (4) optional typing velocity analysis.',
    },
    {
      num: '04',
      title: 'Deterministic Evidence Synthesis',
      icon: CheckCircle,
      desc: 'Findings are categorized into High, Medium, or Low evidence confidence according to transparent, pre-established rules. Canary details exact text excerpts, character offsets, peer group sizes, and methodological caveats.',
    },
    {
      num: '05',
      title: 'Human Review & Multi-Format Export',
      icon: FileOutput,
      desc: 'Reviewers access findings via private, 256-bit encrypted secret links. Export standalone offline HTML reports (zero CDN dependencies), sanitized CSV files (formula-injection protected), or JSON. Cascade delete records at any time.',
    },
  ];

  return (
    <div className="py-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="mb-12 text-center">
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">5-Step Architecture</span>
        <h1 className="font-editorial text-4xl sm:text-5xl text-[#1C1917] mt-2 mb-4">How Canary Audits Human Datasets</h1>
        <p className="text-sm text-[#78716C] max-w-2xl mx-auto leading-relaxed">
          From task design to post-hoc review, Canary provides a rigorous, privacy-respecting audit trail that assists reviewers without jumping to automated conclusions.
        </p>
      </div>

      <div className="space-y-8 mb-16">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <div key={step.num} className="canary-card p-6 sm:p-8 flex flex-col sm:flex-row gap-6 items-start">
              <div className="flex sm:flex-col items-center gap-3 shrink-0">
                <span className="font-mono text-2xl font-bold text-[#D6D3D1]">{step.num}</span>
                <div className="w-10 h-10 rounded-md bg-[#F4EFEA] border border-[#E7E5E4] flex items-center justify-center text-[#1C1917]">
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div>
                <h3 className="font-editorial text-2xl font-medium text-[#1C1917] mb-2">{step.title}</h3>
                <p className="text-sm text-[#44403C] leading-relaxed">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="canary-card p-8 bg-[#FAF5EE] border-[#E8DEC8] text-center">
        <h2 className="font-editorial text-2xl text-[#1C1917] mb-3">Begin with Task Preparation</h2>
        <p className="text-xs text-[#785E2F] max-w-lg mx-auto mb-6">
          If you have not distributed your tasks yet, generate canary markers now to maximize detection accuracy.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/prepare"
            className="px-5 py-2.5 rounded-md bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors inline-flex items-center gap-1.5"
          >
            Prepare Tasks with Markers <ArrowRight className="w-3.5 h-3.5" />
          </Link>
          <Link
            to="/audit"
            className="px-5 py-2.5 rounded-md bg-white border border-[#D6D3D1] text-[#1C1917] text-xs font-medium hover:bg-[#F4EFEA] transition-colors"
          >
            Audit Existing Dataset
          </Link>
        </div>
      </div>
    </div>
  );
};
