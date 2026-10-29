import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';

interface EvaluationArtifact {
  dataset_version: string;
  sample_size: number;
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
  tpr: number;
  fpr: number;
  tpr_ci_lower: number;
  tpr_ci_upper: number;
  fpr_ci_lower: number;
  fpr_ci_upper: number;
  ci_method: string;
  timestamp: string;
}

export const AccuracyPage: React.FC = () => {
  const [evaluation, setEvaluation] = useState<EvaluationArtifact | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Attempt to load latest verified evaluation artifact from API
    fetch('/api/v1/accuracy/latest')
      .then((res) => {
        if (!res.ok) throw new Error('Not available');
        return res.json();
      })
      .then((data) => {
        setEvaluation(data);
        setLoading(false);
      })
      .catch(() => {
        setEvaluation(null);
        setLoading(false);
      });
  }, []);

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="mb-10 text-center">
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">Empirical Benchmarks</span>
        <h1 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] mt-1 mb-2">Measured Accuracy & Evaluation</h1>
        <p className="text-sm text-[#78716C] max-w-2xl mx-auto leading-relaxed">
          Canary evaluates detection rates and false-positive rates on ground-truth benchmark datasets using Wilson score confidence intervals. We report real measured values rather than speculative claims.
        </p>
      </div>

      {loading ? (
        <div className="py-16 text-center text-xs text-[#78716C]">Loading evaluation records...</div>
      ) : evaluation ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="canary-card p-6">
              <span className="text-xs font-mono uppercase text-[#78716C]">True Positive Rate (TPR / Recall)</span>
              <div className="font-editorial text-4xl font-medium text-[#1C1917] mt-2">
                {(evaluation.tpr * 100).toFixed(1)}%
              </div>
              <span className="text-xs font-mono text-[#78716C] mt-1 block">
                95% CI: [{(evaluation.tpr_ci_lower * 100).toFixed(1)}%, {(evaluation.tpr_ci_upper * 100).toFixed(1)}%] ({evaluation.ci_method})
              </span>
            </div>

            <div className="canary-card p-6">
              <span className="text-xs font-mono uppercase text-[#78716C]">False Positive Rate (FPR)</span>
              <div className="font-editorial text-4xl font-medium text-[#1C1917] mt-2">
                {(evaluation.fpr * 100).toFixed(1)}%
              </div>
              <span className="text-xs font-mono text-[#78716C] mt-1 block">
                95% CI: [{(evaluation.fpr_ci_lower * 100).toFixed(1)}%, {(evaluation.fpr_ci_upper * 100).toFixed(1)}%] ({evaluation.ci_method})
              </span>
            </div>
          </div>

          <div className="canary-card p-6 space-y-3">
            <h3 className="text-xs font-semibold text-[#1C1917] uppercase tracking-wider font-mono">Evaluation Metadata</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono text-[#44403C]">
              <div>Sample Size: <strong>{evaluation.sample_size}</strong></div>
              <div>Dataset: <strong>{evaluation.dataset_version}</strong></div>
              <div>TP / FP: <strong>{evaluation.true_positives} / {evaluation.false_positives}</strong></div>
              <div>TN / FN: <strong>{evaluation.true_negatives} / {evaluation.false_negatives}</strong></div>
            </div>
          </div>
        </div>
      ) : (
        /* Authoritative required state when no evaluation artifact is found */
        <div className="canary-card p-12 text-center max-w-xl mx-auto space-y-4">
          <div className="w-12 h-12 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mx-auto border border-[#E8DEC8]">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="font-editorial text-2xl text-[#1C1917]">Evaluation results are not available yet.</h2>
          <p className="text-xs text-[#78716C] leading-relaxed max-w-md mx-auto">
            To view benchmark accuracy, run the reproducible evaluation command <code className="bg-[#F4EFEA] px-1.5 py-0.5 rounded text-[#1C1917]">python scripts/evaluate.py</code> in the repository. Canary never fabricates synthetic benchmark numbers.
          </p>
        </div>
      )}
    </div>
  );
};
