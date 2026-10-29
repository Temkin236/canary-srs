import React from 'react';
import { ShieldCheck, Clock, EyeOff, Lock } from 'lucide-react';

export const PrivacyPage: React.FC = () => {
  return (
    <div className="py-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      <div>
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">Transparency</span>
        <h1 className="font-editorial text-4xl text-[#1C1917] mt-1 mb-3">Privacy & Data Retention Policy</h1>
        <p className="text-sm text-[#78716C] leading-relaxed">
          Canary is built on the principle of data minimization, zero model training on user submissions, and strict ephemeral storage.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div className="canary-card p-6 space-y-2">
          <div className="w-8 h-8 rounded bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mb-2">
            <Clock className="w-4 h-4" />
          </div>
          <h3 className="font-editorial text-xl text-[#1C1917]">7-Day Ephemeral Retention</h3>
          <p className="text-xs text-[#44403C] leading-relaxed">
            All uploaded files, worker responses, generated reference answers, and audit findings are scheduled for permanent, unrecoverable deletion after 7 calendar days.
          </p>
        </div>

        <div className="canary-card p-6 space-y-2">
          <div className="w-8 h-8 rounded bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mb-2">
            <Lock className="w-4 h-4" />
          </div>
          <h3 className="font-editorial text-xl text-[#1C1917]">Immediate "Delete Now"</h3>
          <p className="text-xs text-[#44403C] leading-relaxed">
            Reviewers can invoke the "Delete Now" button on any audit results page to instantly purge all records, database rows, and files immediately without waiting for the retention timer.
          </p>
        </div>

        <div className="canary-card p-6 space-y-2">
          <div className="w-8 h-8 rounded bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mb-2">
            <EyeOff className="w-4 h-4" />
          </div>
          <h3 className="font-editorial text-xl text-[#1C1917]">No External AI Egress Without Consent</h3>
          <p className="text-xs text-[#44403C] leading-relaxed">
            Canary defaults to 100% offline analysis. Your dataset is never shared with OpenAI, Google Gemini, Anthropic, or any third party unless you explicitly opt in for external reference checks.
          </p>
        </div>

        <div className="canary-card p-6 space-y-2">
          <div className="w-8 h-8 rounded bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mb-2">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <h3 className="font-editorial text-xl text-[#1C1917]">Zero Secret Link Persistence</h3>
          <p className="text-xs text-[#44403C] leading-relaxed">
            Only SHA-256 cryptographic hashes of audit secret tokens are stored in the database. Raw tokens exist only in the reviewer's browser session.
          </p>
        </div>
      </div>
    </div>
  );
};
