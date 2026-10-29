import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const TermsPage: React.FC = () => {
  return (
    <div className="py-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      <div>
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">Governance</span>
        <h1 className="font-editorial text-4xl text-[#1C1917] mt-1 mb-3">Responsible-Use Terms</h1>
        <p className="text-sm text-[#78716C] leading-relaxed">
          Canary is designed to safeguard dataset integrity while upholding labor fairness, human accountability, and procedural ethics.
        </p>
      </div>

      <div className="p-6 rounded-lg bg-[#FAF5EE] border border-[#E8DEC8] space-y-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-[#B8860B] shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-[#5C451D] mb-1">Mandatory Usage Constraints</h3>
            <p className="text-xs text-[#785E2F] leading-relaxed">
              By using Canary, you agree to the following non-negotiable ethical constraints:
            </p>
          </div>
        </div>

        <ul className="space-y-3 text-xs text-[#5C451D] pl-8 list-disc">
          <li>
            <strong>No Automated Penalties:</strong> You must never configure systems to automatically reject, ban, suspend, or withhold compensation from a worker based solely on Canary findings.
          </li>
          <li>
            <strong>Human Adjudication Required:</strong> Every finding must be inspected by a qualified human reviewer who considers context, task ambiguity, and worker intent.
          </li>
          <li>
            <strong>No Stylometric Extrapolation:</strong> You may not use Canary outputs to assert definitive claims about an individual's personal writing style or cognitive ability.
          </li>
          <li>
            <strong>Public Anonymity:</strong> You agree not to publish, dox, or publicize individual worker IDs or private worker answers in association with contamination flags.
          </li>
        </ul>
      </div>
    </div>
  );
};
