import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Users, Zap, AlertTriangle, ArrowRight, EyeOff, ShieldCheck, Lock, Cpu, Sparkles, CheckCircle2 } from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <div className="flex flex-col">
      {/* Hero Section with Ambient Background */}
      <section className="relative overflow-hidden pt-16 pb-20 md:pt-24 md:pb-28 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto text-center">
        {/* Subtle decorative glowing backdrops */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-gradient-to-tr from-[#B8860B]/10 via-[#FAF5EE]/40 to-transparent blur-3xl pointer-events-none -z-10 rounded-full" />
        
        {/* Top Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/90 border border-[#E7E5E4] text-[#78716C] text-xs font-mono uppercase tracking-wider mb-6 shadow-xs backdrop-blur-sm">
          <span className="w-2 h-2 rounded-full bg-[#B8860B] animate-pulse"></span>
          Privacy-First Dataset Contamination Audit
        </div>

        <h1 className="font-editorial text-4xl sm:text-5xl md:text-6xl text-[#1C1917] tracking-tight leading-[1.12] mb-6 max-w-4xl mx-auto">
          Canary finds evidence that human-written dataset answers may have been contaminated by chatbot output.
        </h1>

        <p className="text-lg sm:text-xl text-[#44403C] max-w-3xl mx-auto mb-10 leading-relaxed font-sans font-light">
          Built for dataset stewards, crowd platforms, and ML researchers. Canary systematically detects hidden task markers, compares answers against AI reference distributions, and uncovers cross-worker duplicates.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-14">
          <Link
            to="/audit"
            className="w-full sm:w-auto px-7 py-3.5 rounded-lg bg-[#1C1917] text-[#FAF8F5] font-medium text-sm hover:bg-[#292524] transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2 group"
          >
            Start an Audit
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            to="/prepare"
            className="w-full sm:w-auto px-7 py-3.5 rounded-lg bg-white border border-[#D6D3D1] text-[#1C1917] font-medium text-sm hover:bg-[#F4EFEA] transition-all shadow-xs flex items-center justify-center gap-2"
          >
            Prepare Tasks with Markers
          </Link>
          <Link
            to="/results/synthetic-demo-audit"
            className="w-full sm:w-auto px-5 py-3.5 rounded-lg bg-transparent border border-transparent text-[#78716C] hover:text-[#1C1917] font-medium text-sm transition-colors flex items-center justify-center gap-1.5"
          >
            <Sparkles className="w-4 h-4 text-[#B8860B]" />
            Explore Synthetic Demo
          </Link>
        </div>

        {/* Hero Visual Asset Showcase */}
        <div className="relative max-w-4xl mx-auto mb-14 group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#B8860B]/20 via-[#1C1917]/10 to-[#B8860B]/20 rounded-2xl blur-lg opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative rounded-2xl overflow-hidden border border-[#E7E5E4] shadow-2xl bg-[#1C1917]/5">
            <img 
              src="/images/canary_hero_visual.jpg" 
              alt="Canary AI Dataset Contamination Audit Platform" 
              className="w-full h-auto object-cover transform hover:scale-[1.01] transition-transform duration-500" 
            />
            {/* Overlay Glass Tags */}
            <div className="absolute bottom-4 left-4 right-4 flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl canary-glass text-xs text-[#44403C] shadow-lg">
              <div className="flex items-center gap-2 font-mono text-[11px]">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span className="font-semibold text-[#1C1917]">Deterministic Pipeline Active</span>
                <span className="text-[#A8A29E]">|</span>
                <span>Zero-Width Steganography</span>
              </div>
              <div className="flex items-center gap-2 text-[11px] font-mono text-[#78716C]">
                <span>MinHash Jaccard</span>
                <span className="text-[#A8A29E]">•</span>
                <span>SHA-256 Hashing</span>
              </div>
            </div>
          </div>
        </div>

        {/* Invariant Warning Banner */}
        <div className="p-4 rounded-xl bg-[#FAF5EE] border border-[#E8DEC8] text-left max-w-3xl mx-auto flex items-start gap-3.5 shadow-xs">
          <AlertTriangle className="w-5 h-5 text-[#B8860B] shrink-0 mt-0.5" />
          <div className="text-xs text-[#785E2F] leading-relaxed">
            <strong className="font-semibold block text-[#5C451D] mb-0.5">Critical Principle: Evidence, Not Proof</strong>
            Canary produces structured evidence to assist human reviewers. A flag never proves AI authorship, plagiarism, or intentional cheating, and must never be used to automatically reject workers or withhold payment.
          </div>
        </div>
      </section>

      {/* Trust & Architecture Showcase Section */}
      <section className="py-16 bg-white/70 border-t border-[#E7E5E4] px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Shield Visual */}
            <div className="lg:col-span-4 flex flex-col items-center justify-center text-center p-6 rounded-2xl canary-card bg-gradient-to-b from-[#FAF8F5] to-white">
              <div className="w-36 h-36 rounded-full overflow-hidden shadow-lg border-2 border-[#E8DEC8] mb-4">
                <img 
                  src="/images/canary_audit_shield.jpg" 
                  alt="Canary Security Badge" 
                  className="w-full h-full object-cover scale-105" 
                />
              </div>
              <h3 className="font-editorial text-xl font-medium text-[#1C1917] mb-1">Cyber Canary Invariants</h3>
              <p className="text-xs text-[#78716C]">Rigorous cryptographic and ethical guarantees built into every layer</p>
            </div>

            {/* Right Highlights */}
            <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-5 rounded-xl canary-card flex flex-col justify-between">
                <div>
                  <div className="w-9 h-9 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-3">
                    <Cpu className="w-4 h-4" />
                  </div>
                  <h4 className="font-medium text-sm text-[#1C1917] mb-1.5">100% Deterministic & Offline</h4>
                  <p className="text-xs text-[#57534E] leading-relaxed">
                    Zero-width tokens, exact Jaccard clustering, and TF-IDF operate completely offline without external AI services.
                  </p>
                </div>
                <div className="mt-4 pt-2.5 border-t border-[#E7E5E4] flex items-center gap-1.5 text-[11px] font-mono text-emerald-700">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Zero Data Leakage
                </div>
              </div>

              <div className="p-5 rounded-xl canary-card flex flex-col justify-between">
                <div>
                  <div className="w-9 h-9 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-3">
                    <Lock className="w-4 h-4" />
                  </div>
                  <h4 className="font-medium text-sm text-[#1C1917] mb-1.5">Ephemeral 7-Day Purge</h4>
                  <p className="text-xs text-[#57534E] leading-relaxed">
                    Uploaded dataset records automatically expire and undergo hard cascading deletion after 7 days, or instant manual purge.
                  </p>
                </div>
                <div className="mt-4 pt-2.5 border-t border-[#E7E5E4] flex items-center gap-1.5 text-[11px] font-mono text-emerald-700">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Automatic Expiration
                </div>
              </div>

              <div className="p-5 rounded-xl canary-card flex flex-col justify-between">
                <div>
                  <div className="w-9 h-9 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-3">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <h4 className="font-medium text-sm text-[#1C1917] mb-1.5">No Automated Penalties</h4>
                  <p className="text-xs text-[#57534E] leading-relaxed">
                    Canary never automatically rejects submissions or withholds worker payments. All findings require human steward adjudication.
                  </p>
                </div>
                <div className="mt-4 pt-2.5 border-t border-[#E7E5E4] flex items-center gap-1.5 text-[11px] font-mono text-emerald-700">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Human-in-the-Loop
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Checks Grid */}
      <section className="py-20 bg-[#F4EFEA]/60 border-t border-b border-[#E7E5E4] px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] mb-3">Four Multi-Modal Detection Checks</h2>
            <p className="text-sm text-[#78716C]">
              Engineered for deterministic execution, explainable confidence categories, and zero subjective guesswork.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Check 1 */}
            <div className="canary-card p-6 flex flex-col justify-between hover:shadow-lg transition-all">
              <div>
                <div className="w-10 h-10 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
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
            <div className="canary-card p-6 flex flex-col justify-between hover:shadow-lg transition-all">
              <div>
                <div className="w-10 h-10 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
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
            <div className="canary-card p-6 flex flex-col justify-between hover:shadow-lg transition-all">
              <div>
                <div className="w-10 h-10 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
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
            <div className="canary-card p-6 flex flex-col justify-between hover:shadow-lg transition-all">
              <div>
                <div className="w-10 h-10 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] flex items-center justify-center text-[#B8860B] mb-4">
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
      <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto text-center">
        <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] mb-4">Ready to audit your human-written dataset?</h2>
        <p className="text-sm sm:text-base text-[#44403C] max-w-xl mx-auto mb-10 leading-relaxed font-light">
          Upload standard CSV or JSONL files. Get private, encrypted results with offline standalone HTML, CSV, and JSON exports.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/audit"
            className="px-7 py-3.5 rounded-lg bg-[#1C1917] text-[#FAF8F5] text-sm font-medium hover:bg-[#292524] transition-all shadow-md hover:shadow-lg flex items-center gap-2"
          >
            Upload Dataset
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/how-it-works"
            className="px-7 py-3.5 rounded-lg bg-white border border-[#D6D3D1] text-[#1C1917] text-sm font-medium hover:bg-[#F4EFEA] transition-colors shadow-xs"
          >
            Read Methodology Guide
          </Link>
        </div>
      </section>
    </div>
  );
};
