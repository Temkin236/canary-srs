import React, { useState } from 'react';
import { Send, CheckCircle2 } from 'lucide-react';

export const ContactPage: React.FC = () => {
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="py-16 px-4 sm:px-6 lg:px-8 max-w-xl mx-auto">
      <div className="text-center mb-8">
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">Inquiries</span>
        <h1 className="font-editorial text-4xl text-[#1C1917] mt-1 mb-2">Contact & Feedback</h1>
        <p className="text-sm text-[#78716C]">
          Questions regarding audit methodology, research partnerships, or security reports.
        </p>
      </div>

      {submitted ? (
        <div className="canary-card p-8 text-center space-y-3">
          <CheckCircle2 className="w-10 h-10 text-green-600 mx-auto" />
          <h2 className="font-editorial text-2xl text-[#1C1917]">Message Received</h2>
          <p className="text-xs text-[#78716C]">
            Thank you for reaching out. We will review your note and respond promptly.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="canary-card p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#1C1917] mb-1">Your Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full text-xs p-2.5 rounded border border-[#D6D3D1] bg-white focus:outline-none focus:ring-1 focus:ring-[#1C1917]"
              placeholder="e.g. Dr. Alex Mercer"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#1C1917] mb-1">Email Address</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full text-xs p-2.5 rounded border border-[#D6D3D1] bg-white focus:outline-none focus:ring-1 focus:ring-[#1C1917]"
              placeholder="alex@research.org"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#1C1917] mb-1">Message</label>
            <textarea
              rows={4}
              required
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="w-full text-xs p-2.5 rounded border border-[#D6D3D1] bg-white focus:outline-none focus:ring-1 focus:ring-[#1C1917]"
              placeholder="Your inquiry or feedback regarding Canary SRS..."
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-md bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors flex items-center justify-center gap-2"
          >
            <Send className="w-3.5 h-3.5" /> Send Message
          </button>
        </form>
      )}
    </div>
  );
};
