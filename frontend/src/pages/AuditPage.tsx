import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, CheckCircle, ArrowRight } from 'lucide-react';
import { ValidationResult } from '../types';

export const AuditPage: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [consentAi, setConsentAi] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  const [isValidating, setIsValidating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setErrorMessage(null);
    setIsValidating(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await fetch('/api/v1/audits/validate', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Validation error: ${res.statusText}`);
      }

      const data: ValidationResult = await res.json();
      setValidationResult(data);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to validate dataset.');
      setValidationResult(null);
    } finally {
      setIsValidating(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleStartAudit = async () => {
    if (!file) return;
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('consent_external_ai', String(consentAi));

      const res = await fetch('/api/v1/audits', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail?.message || errData.detail || 'Audit creation failed.');
      }

      const data = await res.json();
      navigate(`/results/${data.secret_token}`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to start audit job.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">Phase 2: Execution</span>
        <h1 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] mt-1 mb-2">Upload Dataset & Run Audit</h1>
        <p className="text-sm text-[#78716C] max-w-2xl">
          Upload human-written crowd responses in CSV or JSONL format. All uploaded data is processed under strict 7-day ephemeral retention.
        </p>
      </div>

      <div className="space-y-6">
        {/* Upload Dropzone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`canary-card p-8 border-2 border-dashed text-center transition-colors ${
            isDragOver ? 'border-[#1C1917] bg-[#FAF5EE]' : 'border-[#D6D3D1] bg-white'
          }`}
        >
          <div className="w-12 h-12 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mx-auto mb-4 border border-[#E8DEC8]">
            <UploadCloud className="w-6 h-6" />
          </div>

          <h3 className="font-editorial text-xl font-medium text-[#1C1917] mb-1">
            {file ? file.name : 'Select or drag & drop dataset file'}
          </h3>
          <p className="text-xs text-[#78716C] mb-4">
            Supported formats: CSV, JSONL (Max size: 10 MB, up to 10,000 answers)
          </p>

          <input
            type="file"
            id="dataset-upload"
            accept=".csv,.jsonl"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileSelect(e.target.files[0]);
              }
            }}
            className="hidden"
          />
          <label
            htmlFor="dataset-upload"
            className="px-4 py-2 rounded-md bg-[#1C1917] text-[#FAF8F5] text-xs font-medium cursor-pointer hover:bg-[#292524] transition-colors inline-block"
          >
            {isValidating ? 'Validating dataset...' : file ? 'Replace File' : 'Browse Files'}
          </label>
        </div>

        {errorMessage && (
          <div className="p-4 rounded-md bg-red-50 border border-red-200 text-xs text-red-800">
            <strong>Validation Error:</strong> {errorMessage}
          </div>
        )}

        {/* Validation Preview Card */}
        {validationResult && (
          <div className="canary-card p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#E7E5E4]">
              <div className="flex items-center gap-2 text-xs font-medium text-green-700">
                <CheckCircle className="w-4 h-4 text-green-600" />
                Valid Dataset Structure ({validationResult.total_rows} answers)
              </div>
              <div className="flex gap-4 text-xs font-mono text-[#78716C]">
                <span>Tasks: {validationResult.tasks_count}</span>
                <span>Workers: {validationResult.workers_count}</span>
              </div>
            </div>

            <div className="text-xs text-[#44403C]">
              <span className="font-semibold block mb-2">Detected Column Mappings:</span>
              <div className="flex flex-wrap gap-2">
                {validationResult.detected_columns.map((col) => (
                  <span key={col} className="px-2.5 py-1 rounded bg-[#F4EFEA] font-mono text-[11px] text-[#44403C]">
                    {col}
                  </span>
                ))}
              </div>
            </div>

            {/* Privacy & External AI Consent */}
            <div className="p-4 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] space-y-2 mt-4">
              <label className="flex items-start gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consentAi}
                  onChange={(e) => setConsentAi(e.target.checked)}
                  className="mt-0.5 rounded text-[#1C1917] focus:ring-0"
                />
                <span className="text-xs text-[#5C451D] leading-relaxed">
                  <strong>Explicit Consent for External AI Reference Similarity:</strong> I consent to comparing task prompts against external AI models (Gemini). If unchecked, Canary runs in 100% Offline Mode (using markers, duplicates, and local lexical checks only).
                </span>
              </label>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                onClick={handleStartAudit}
                disabled={isSubmitting}
                className="px-6 py-2.5 rounded-md bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors flex items-center gap-2"
              >
                {isSubmitting ? 'Starting...' : 'Run Contamination Audit'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
