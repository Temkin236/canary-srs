import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="py-24 px-4 max-w-md mx-auto text-center space-y-4">
      <div className="w-12 h-12 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mx-auto border border-[#E8DEC8]">
        <ShieldAlert className="w-6 h-6" />
      </div>
      <h1 className="font-editorial text-4xl text-[#1C1917]">Page Not Found</h1>
      <p className="text-xs text-[#78716C] leading-relaxed">
        The requested page or secret audit link could not be found, or has expired under the 7-day retention policy.
      </p>
      <div className="pt-2">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Return Home
        </Link>
      </div>
    </div>
  );
};
