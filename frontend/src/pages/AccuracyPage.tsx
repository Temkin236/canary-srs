import React, { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle2, Terminal } from 'lucide-react';

interface EvaluationArtifact {
  dataset_version: string;
  evaluated_at?: string;
  sample_size: number;
  confusion_matrix: {
    true_positives: number;
    false_positives: number;
    true_negatives: number;
    false_negatives: number;
  };
  metrics: {
    tpr: number;
    fpr: number;
    tpr_ci_lower: number;
    tpr_ci_upper: number;
    fpr_ci_lower: number;
    fpr_ci_upper: number;
    ci_method: string;
    confidence_level: number;
  };
  checks_tested?: string[];
  reproduction_command?: string;
  notice?: string;
}

export const AccuracyPage: React.FC = () => {
  const [evaluation, setEvaluation] = useState<EvaluationArtifact | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">
          Empirical Benchmarks
        </span>
        <h1 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] mt-1 mb-2">
          Measured Accuracy & Evaluation
        </h1>
        <p className="text-sm text-[#78716C] max-w-2xl mx-auto leading-relaxed">
          Canary evaluates detection rates and false-positive rates on ground-truth benchmark datasets
          using Wilson score confidence intervals. We report real measured values rather than speculative claims.
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
                {(evaluation.metrics.tpr * 100).toFixed(1)}%
              </div>
              <span className="text-xs font-mono text-[#78716C] mt-1 block">
                95% CI: [{(evaluation.metrics.tpr_ci_lower * 100).toFixed(1)}%, {(evaluation.metrics.tpr_ci_upper * 100).toFixed(1)}%] ({evaluation.metrics.ci_method})
              </span>
            </div>

            <div className="canary-card p-6">
              <span className="text-xs font-mono uppercase text-[#78716C]">False Positive Rate (FPR)</span>
              <div className="font-editorial text-4xl font-medium text-[#1C1917] mt-2">
                {(evaluation.metrics.fpr * 100).toFixed(1)}%
              </div>
              <span className="text-xs font-mono text-[#78716C] mt-1 block">
                95% CI: [{(evaluation.metrics.fpr_ci_lower * 100).toFixed(1)}%, {(evaluation.metrics.fpr_ci_upper * 100).toFixed(1)}%] ({evaluation.metrics.ci_method})
              </span>
            </div>
          </div>

          <div className="canary-card p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#E8DEC8] pb-3">
              <h3 className="text-xs font-semibold text-[#1C1917] uppercase tracking-wider font-mono">
                Confusion Matrix (Ground Truth Benchmark)
              </h3>
              <span className="text-xs font-mono text-[#78716C]">Sample Size: n = {evaluation.sample_size}</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono text-[#44403C]">
              <div className="p-3 bg-[#FAF7F2] rounded border border-[#E8DEC8]">
                <div className="text-[#78716C]">True Positives (TP)</div>
                <div className="text-lg font-bold text-[#1C1917] mt-0.5">{evaluation.confusion_matrix.true_positives}</div>
              </div>
              <div className="p-3 bg-[#FAF7F2] rounded border border-[#E8DEC8]">
                <div className="text-[#78716C]">False Positives (FP)</div>
                <div className="text-lg font-bold text-[#1C1917] mt-0.5">{evaluation.confusion_matrix.false_positives}</div>
              </div>
              <div className="p-3 bg-[#FAF7F2] rounded border border-[#E8DEC8]">
                <div className="text-[#78716C]">True Negatives (TN)</div>
                <div className="text-lg font-bold text-[#1C1917] mt-0.5">{evaluation.confusion_matrix.true_negatives}</div>
              </div>
              <div className="p-3 bg-[#FAF7F2] rounded border border-[#E8DEC8]">
                <div className="text-[#78716C]">False Negatives (FN)</div>
                <div className="text-lg font-bold text-[#1C1917] mt-0.5">{evaluation.confusion_matrix.false_negatives}</div>
              </div>
            </div>
          </div>

          <div className="canary-card p-6 space-y-3">
            <h3 className="text-xs font-semibold text-[#1C1917] uppercase tracking-wider font-mono">
              Evaluation Metadata & Reproducibility
            </h3>
            <div className="space-y-2 text-xs font-mono text-[#44403C]">
              <div>Dataset: <strong className="text-[#1C1917]">{evaluation.dataset_version}</strong></div>
              {evaluation.evaluated_at && (
                <div>Evaluated At: <span className="text-[#78716C]">{new Date(evaluation.evaluated_at).toLocaleString()}</span></div>
              )}
              {evaluation.checks_tested && (
                <div className="flex items-center gap-2 pt-1">
                  <span className="text-[#78716C]">Active Checks:</span>
                  {evaluation.checks_tested.map((chk) => (
                    <span key={chk} className="px-2 py-0.5 bg-[#E8DEC8] text-[#1C1917] rounded text-[11px] font-mono">
                      {chk}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {evaluation.reproduction_command && (
              <div className="pt-3 border-t border-[#E8DEC8] mt-3">
                <span className="text-xs text-[#78716C] block mb-1">Reproduce Benchmark Locally:</span>
                <div className="flex items-center gap-2 bg-[#1C1917] text-[#FAF7F2] px-3 py-2 rounded font-mono text-xs overflow-x-auto">
                  <Terminal className="w-3.5 h-3.5 text-[#B8860B] shrink-0" />
                  <code>{evaluation.reproduction_command}</code>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 bg-[#FAF7F2] border border-[#E8DEC8] rounded text-xs text-[#78716C] flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-[#B8860B] shrink-0 mt-0.5" />
            <p>
              {evaluation.notice || 'Empirical evaluation results generated under reproducible benchmark conditions. Findings serve as human-review evidence and are subject to Wilson confidence bounds.'}
            </p>
          </div>
        </div>
      ) : (
        <div className="canary-card p-12 text-center max-w-xl mx-auto space-y-4">
          <div className="w-12 h-12 rounded-full bg-[#FAF5EE] text-[#B8860B] flex items-center justify-center mx-auto border border-[#E8DEC8]">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="font-editorial text-2xl text-[#1C1917]">Evaluation results are not available yet.</h2>
          <p className="text-xs text-[#78716C] leading-relaxed max-w-md mx-auto">
            To view benchmark accuracy, run the reproducible evaluation command{' '}
            <code className="bg-[#F4EFEA] px-1.5 py-0.5 rounded text-[#1C1917]">uv run python scripts/evaluate.py</code>{' '}
            in the repository. Canary never fabricates synthetic benchmark numbers.
          </p>
        </div>
      )}
    </div>
  );
};
