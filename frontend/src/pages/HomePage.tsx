import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Users, Zap, AlertTriangle, ArrowRight, EyeOff } from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="py-20 md:py-28 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#F4EFEA] border border-[#E7E5E4] text-[#78716C] text-xs font-mono uppercase tracking-wider mb-6">
          <span className="w-2 h-2 rounded-full bg-[#B8860B] animate-pulse"></span>
          Audit & Evidence Collection Tool
        </div>

        <h1 className="font-editorial text-4xl sm:text-5xl md:text-6xl text-[#1C1917] tracking-tight leading-[1.15] mb-6">
          Canary finds evidence that human-written dataset answers may have been contaminated by chatbot output.
        </h1>

        <p className="text-lg sm:text-xl text-[#44403C] max-w-3xl mx-auto mb-10 leading-relaxed font-sans font-light">
          Built for dataset stewards, crowd platforms, and ML researchers. Canary systematically detects hidden task markers, compares answers against AI reference distributions, and uncovers cross-worker duplicates.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
          <Link
            to="/audit"
            className="w-full sm:w-auto px-6 py-3.5 rounded-md bg-[#1C1917] text-[#FAF8F5] font-medium text-sm hover:bg-[#292524] transition-all shadow-sm flex items-center justify-center gap-2 group"
          >
            Start an Audit
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </Link>
          <Link
            to="/prepare"
            className="w-full sm:w-auto px-6 py-3.5 rounded-md bg-white border border-[#D6D3D1] text-[#1C1917] font-medium text-sm hover:bg-[#F4EFEA] transition-colors shadow-sm flex items-center justify-center gap-2"
          >
            Prepare Tasks with Markers
          </Link>
          <Link
            to="/results/synthetic-demo-audit"
            className="w-full sm:w-auto px-6 py-3.5 rounded-md bg-transparent border border-transparent text-[#78716C] hover:text-[#1C1917] font-medium text-sm transition-colors flex items-center justify-center gap-2"
          >
            Explore Synthetic Example
          </Link>
        </div>

        {/* Invariant Warning Banner */}
        <div className="p-4 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] text-left max-w-2xl mx-auto flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-[#B8860B] shrink-0 mt-0.5" />
          <div className="text-xs text-[#785E2F] leading-relaxed">
            <strong className="font-semibold block text-[#5C451D] mb-0.5">Critical Principle: Evidence, Not Proof</strong>
            Canary produces structured evidence to assist human reviewers. A flag never proves AI authorship, plagiarism, or intentional cheating, and must never be used to automatically reject workers or withhold payment.
          </div>
        </div>
      </section>

      {/* Core Checks Grid */}
      <section className="py-16 bg-[#F4EFEA]/60 border-t border-b border-[#E7E5E4] px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-editorial text-3xl text-[#1C1917] mb-3">Four Multi-Modal Detection Checks</h2>
            <p className="text-sm text-[#78716C]">
              Engineered for deterministic execution, explainable confidence categories, and zero subjective guesswork.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Check 1 */}
            <div className="canary-card p-6 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
                  <EyeOff className="w-5 h-5" />
                </div>
                <h3 className="font-editorial text-xl font-medium text-[#1C1917] mb-2">1. Task-Specific Marker Detection</h3>
                <p className="text-xs text-[#44403C] leading-relaxed mb-4">
                  Injects cryptographically unique tokens via zero-width Unicode sequences or subtle instruction prompts. If a worker pastes the prompt into an LLM, the model echoes the marker into the answer.
                </p>
              </div>
              <div className="pt-3 border-t border-[#E7E5E4] flex items-center justify-between text-[11px] font-mono text-[#78716C]">
                <span>Matching: Exact + Typo Bounded</span>
                <span className="text-[#B8860B] font-semibold">High Confidence</span>
              </div>
            </div>

            {/* Check 2 */}
            <div className="canary-card p-6 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
                  <Search className="w-5 h-5" />
                </div>
                <h3 className="font-editorial text-xl font-medium text-[#1C1917] mb-2">2. Reference Similarity & Peer Distribution</h3>
                <p className="text-xs text-[#44403C] leading-relaxed mb-4">
                  Evaluates lexical (TF-IDF) and semantic similarity against AI reference answers, contextualized by the peer answer distribution for the task. High raw similarity alone is treated with caution.
                </p>
              </div>
              <div className="pt-3 border-t border-[#E7E5E4] flex items-center justify-between text-[11px] font-mono text-[#78716C]">
                <span>Comparison: Peer Percentiles</span>
                <span className="text-[#44403C] font-semibold">Medium / Low Confidence</span>
              </div>
            </div>

            {/* Check 3 */}
            <div className="canary-card p-6 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
                  <Users className="w-5 h-5" />
                </div>
                <h3 className="font-editorial text-xl font-medium text-[#1C1917] mb-2">3. Cross-Worker Duplicate Detection</h3>
                <p className="text-xs text-[#44403C] leading-relaxed mb-4">
                  Identifies identical or near-duplicate answers submitted by different workers for the same task. Detects bot syndicates or multiple workers copying identical default chatbot answers.
                </p>
              </div>
              <div className="pt-3 border-t border-[#E7E5E4] flex items-center justify-between text-[11px] font-mono text-[#78716C]">
                <span>Clustering: MinHash / Token Jaccard</span>
                <span className="text-[#44403C] font-semibold">Medium / High (with AI)</span>
              </div>
            </div>

            {/* Check 4 */}
            <div className="canary-card p-6 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
                  <Zap className="w-5 h-5" />
                </div>
                <h3 className="font-editorial text-xl font-medium text-[#1C1917] mb-2">4. Speed Plausibility Check (Optional)</h3>
                <p className="text-xs text-[#44403C] leading-relaxed mb-4">
                  When timing metadata is present, checks whether answer length exceeds human typing velocity thresholds (&gt;15 characters per second). Automatically skipped when timing is absent.
                </p>
              </div>
              <div className="pt-3 border-t border-[#E7E5E4] flex items-center justify-between text-[11px] font-mono text-[#78716C]">
                <span>Threshold: &gt;15 chars/sec</span>
                <span className="text-[#78716C] font-semibold">Low Confidence (Auxiliary)</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto text-center">
        <h2 className="font-editorial text-3xl text-[#1C1917] mb-4">Ready to audit your human-written dataset?</h2>
        <p className="text-sm text-[#44403C] max-w-xl mx-auto mb-8 leading-relaxed">
          Upload standard CSV or JSONL files. Get private, encrypted results with offline standalone HTML, CSV, and JSON exports.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/audit"
            className="px-6 py-3 rounded-md bg-[#1C1917] text-[#FAF8F5] text-sm font-medium hover:bg-[#292524] transition-colors"
          >
            Upload Dataset
          </Link>
          <Link
            to="/how-it-works"
            className="px-6 py-3 rounded-md bg-white border border-[#D6D3D1] text-[#1C1917] text-sm font-medium hover:bg-[#F4EFEA] transition-colors"
          >
            Read Methodology Guide
          </Link>
        </div>
      </section>
    </div>
  );
};
