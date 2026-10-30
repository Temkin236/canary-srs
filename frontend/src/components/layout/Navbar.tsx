import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, Compass, FileText, UploadCloud, BarChart2, LayoutDashboard } from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();

  const navLinks = [
    { to: '/', label: 'Home', icon: ShieldCheck },
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/how-it-works', label: 'How It Works', icon: Compass },
    { to: '/prepare', label: 'Prepare Tasks', icon: FileText },
    { to: '/audit', label: 'Start Audit', icon: UploadCloud },
    { to: '/accuracy', label: 'Accuracy', icon: BarChart2 },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#FAF8F5]/90 backdrop-blur-md border-b border-[#E7E5E4]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-full bg-[#1C1917] text-[#FAF8F5] flex items-center justify-center font-editorial font-bold text-lg shadow-sm group-hover:bg-[#B8860B] transition-colors">
            C
          </div>
          <div className="flex flex-col">
            <span className="font-editorial text-xl font-medium tracking-tight text-[#1C1917]">Canary</span>
            <span className="text-[10px] text-[#78716C] -mt-1 tracking-wider uppercase font-mono">Dataset Audit</span>
          </div>
        </Link>

        <nav className="flex items-center gap-1 sm:gap-2">
          {navLinks.map((item) => {
            const isActive = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-[#1C1917] text-[#FAF8F5]'
                    : 'text-[#44403C] hover:text-[#1C1917] hover:bg-[#F4EFEA]'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
