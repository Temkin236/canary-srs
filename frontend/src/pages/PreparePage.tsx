import React, { useState } from 'react';
import { Copy, Download, Plus, Trash2, Check, Shield, FileText } from 'lucide-react';
import { PreparedTask } from '../types';

export const PreparePage: React.FC = () => {
  const [tasks, setTasks] = useState<Array<{ id: string; prompt: string }>>([
    {
      id: 'task-01',
      prompt: 'Explain the difference between supervised and unsupervised machine learning in three sentences.',
    },
    {
      id: 'task-02',
      prompt: 'Write a polite follow-up email to a client requesting feedback on a delivered proposal.',
    },
  ]);

  const [hidingMethod, setHidingMethod] = useState<'zero_width' | 'prompt_embedded'>('zero_width');
  const [preparedTasks, setPreparedTasks] = useState<PreparedTask[]>([]);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleAddTask = () => {
    const nextNum = tasks.length + 1;
    setTasks([...tasks, { id: `task-0${nextNum}`, prompt: '' }]);
  };

  const handleRemoveTask = (idx: number) => {
    setTasks(tasks.filter((_, i) => i !== idx));
  };

  const handlePromptChange = (idx: number, prompt: string) => {
    const updated = [...tasks];
    updated[idx].prompt = prompt;
    setTasks(updated);
  };

  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerateError(null);

    try {
      const payload = {
        tasks: tasks.map((t) => ({ task_id: t.id, prompt: t.prompt })),
        hiding_method: hidingMethod,
      };

      const res = await fetch('/api/v1/prepare/markers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Failed to generate markers: ${res.statusText}`);
      }

      const data = await res.json();
      setPreparedTasks(data.tasks);
    } catch (err) {
      setGenerateError(err instanceof Error ? err.message : 'Error generating markers.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleDownloadManifest = () => {
    const manifest = {
      format_version: '1.0',
      created_at: new Date().toISOString(),
      items: preparedTasks.map((pt) => ({
        task_id: pt.task_id,
        marker: pt.marker,
        hiding_method: pt.hiding_method,
      })),
    };

    const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `canary_marker_manifest_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <span className="text-xs font-mono uppercase tracking-wider text-[#B8860B] font-semibold">Phase 1: Seeding</span>
        <h1 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] mt-1 mb-2">Task Preparation & Marker Generation</h1>
        <p className="text-sm text-[#78716C] max-w-2xl">
          Embed task-specific canary markers into your crowd instructions. If a respondent pastes the prompt into a chatbot, the marker is absorbed and echoed back in the response.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Task Editor Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="canary-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-[#1C1917] flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#B8860B]" />
                Define Tasks ({tasks.length})
              </h2>
              <button
                onClick={handleAddTask}
                className="text-xs font-medium text-[#1C1917] hover:text-[#B8860B] flex items-center gap-1 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Add Task
              </button>
            </div>

            <div className="space-y-4">
              {tasks.map((task, idx) => (
                <div key={task.id} className="p-4 rounded-md bg-[#FAF8F5] border border-[#E7E5E4] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-medium text-[#44403C]">{task.id}</span>
                    {tasks.length > 1 && (
                      <button
                        onClick={() => handleRemoveTask(idx)}
                        className="text-[#A8A29E] hover:text-red-600 transition-colors"
                        title="Remove task"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  <textarea
                    rows={2}
                    value={task.prompt}
                    onChange={(e) => handlePromptChange(idx, e.target.value)}
                    placeholder="Enter prompt text or worker instruction..."
                    className="w-full text-xs font-sans rounded border border-[#D6D3D1] p-2.5 bg-white focus:outline-none focus:ring-1 focus:ring-[#1C1917]"
                  />
                </div>
              ))}
            </div>

            {/* Hiding Strategy Selection */}
            <div className="mt-6 pt-6 border-t border-[#E7E5E4]">
              <label className="block text-xs font-semibold text-[#1C1917] mb-2">Marker Hiding Method</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label
                  className={`p-3 rounded-md border text-xs cursor-pointer flex flex-col justify-between transition-colors ${
                    hidingMethod === 'zero_width'
                      ? 'border-[#1C1917] bg-[#FAF5EE]'
                      : 'border-[#E7E5E4] bg-white hover:bg-[#FAF8F5]'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="hidingMethod"
                      value="zero_width"
                      checked={hidingMethod === 'zero_width'}
                      onChange={() => setHidingMethod('zero_width')}
                      className="text-[#1C1917]"
                    />
                    <span className="font-medium text-[#1C1917]">Zero-Width Unicode</span>
                  </div>
                  <span className="text-[11px] text-[#78716C] mt-1 pl-5">
                    Invisible to humans; survives standard clipboard copy-paste in most OS browsers.
                  </span>
                </label>

                <label
                  className={`p-3 rounded-md border text-xs cursor-pointer flex flex-col justify-between transition-colors ${
                    hidingMethod === 'prompt_embedded'
                      ? 'border-[#1C1917] bg-[#FAF5EE]'
                      : 'border-[#E7E5E4] bg-white hover:bg-[#FAF8F5]'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="hidingMethod"
                      value="prompt_embedded"
                      checked={hidingMethod === 'prompt_embedded'}
                      onChange={() => setHidingMethod('prompt_embedded')}
                      className="text-[#1C1917]"
                    />
                    <span className="font-medium text-[#1C1917]">Prompt Footnote</span>
                  </div>
                  <span className="text-[11px] text-[#78716C] mt-1 pl-5">
                    Visible syntactic footnote or reference tag. Guaranteed to be processed by LLMs.
                  </span>
                </label>
              </div>
            </div>

            {generateError && (
              <div className="mt-4 p-3 rounded bg-red-50 border border-red-200 text-xs text-red-700">
                {generateError}
              </div>
            )}

            <div className="mt-6">
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full py-2.5 rounded-md bg-[#1C1917] text-[#FAF8F5] text-xs font-medium hover:bg-[#292524] transition-colors"
              >
                {isGenerating ? 'Generating Markers...' : 'Generate Canary Markers & Prepared Prompts'}
              </button>
            </div>
          </div>
        </div>

        {/* Output & Manifest Column */}
        <div className="space-y-6">
          <div className="canary-card p-6">
            <h2 className="text-base font-semibold text-[#1C1917] mb-2 flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#B8860B]" />
              Marker Manifest
            </h2>
            <p className="text-xs text-[#78716C] mb-4">
              Download this manifest to automatically cross-reference markers when you run the audit later.
            </p>

            {preparedTasks.length === 0 ? (
              <div className="py-8 text-center text-xs text-[#A8A29E] border border-dashed border-[#E7E5E4] rounded-md">
                Click "Generate Canary Markers" to create task manifests.
              </div>
            ) : (
              <div className="space-y-3">
                <button
                  onClick={handleDownloadManifest}
                  className="w-full py-2 rounded-md bg-[#FAF5EE] border border-[#E8DEC8] text-[#785E2F] hover:bg-[#F5ECD9] text-xs font-medium flex items-center justify-center gap-2 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Download manifest.json
                </button>
                <div className="max-h-80 overflow-y-auto space-y-2 pr-1">
                  {preparedTasks.map((pt, idx) => (
                    <div key={pt.task_id} className="p-2.5 rounded border border-[#E7E5E4] bg-white text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-medium text-[#1C1917]">{pt.task_id}</span>
                        <button
                          onClick={() => handleCopy(pt.prepared_prompt, idx)}
                          className="text-[#78716C] hover:text-[#1C1917] flex items-center gap-1 font-mono text-[10px]"
                        >
                          {copiedIndex === idx ? (
                            <>
                              <Check className="w-3 h-3 text-green-600" /> Copied
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" /> Copy Prompt
                            </>
                          )}
                        </button>
                      </div>
                      <div className="font-mono text-[11px] text-[#B8860B]">{pt.marker}</div>
                      <div className="text-[10px] text-[#78716C] truncate">{pt.visible_preview}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
