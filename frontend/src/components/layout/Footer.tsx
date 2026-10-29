import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-[#FAF8F5] border-t border-[#E7E5E4] py-12 text-[#78716C] text-sm mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 pb-8 border-b border-[#E7E5E4]">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-[#1C1917] font-medium">
              <Shield className="w-4 h-4 text-[#B8860B]" />
              <span>Canary — Contamination Audit for Human-Written Datasets</span>
            </div>
            <p className="max-w-xl text-xs text-[#78716C] leading-relaxed">
              Canary is an evidence collection and human-review tool. Findings indicate potential anomalies for human inspection and do not prove AI authorship, fraud, or worker misconduct.
            </p>
          </div>

          <div className="flex flex-wrap gap-6 text-xs font-medium text-[#44403C]">
            <Link to="/how-it-works" className="hover:text-[#1C1917]">How It Works</Link>
            <Link to="/accuracy" className="hover:text-[#1C1917]">Accuracy & Metrics</Link>
            <Link to="/privacy" className="hover:text-[#1C1917]">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-[#1C1917]">Responsible Use Terms</Link>
            <Link to="/contact" className="hover:text-[#1C1917]">Contact & Feedback</Link>
          </div>
        </div>

        <div className="pt-6 flex flex-col sm:flex-row justify-between items-center text-xs text-[#A8A29E] gap-4">
          <p>© {new Date().getFullYear()} Canary SRS. Open-source audit methodology for dataset integrity.</p>
          <p className="font-mono text-[11px]">7-day ephemeral retention by default</p>
        </div>
      </div>
    </footer>
  );
};
