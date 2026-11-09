import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, Sparkles, BookOpen } from 'lucide-react';
import { RoleItem, SampleResume } from '../types';

interface ResumeUploadStepProps {
  roles: RoleItem[];
  sampleResumes: SampleResume[];
  onUploadFile: (file: File, role: string) => Promise<void>;
  onSelectSample: (sampleId: string, role: string) => Promise<void>;
  isLoading: boolean;
  error?: string | null;
}

export const ResumeUploadStep: React.FC<ResumeUploadStepProps> = ({
  roles,
  sampleResumes,
  onUploadFile,
  onSelectSample,
  isLoading,
  error
}) => {
  const [selectedRole, setSelectedRole] = useState<string>('AI/ML Engineer');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFile) {
      onUploadFile(selectedFile, selectedRole);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Intro hero banner */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-100">
          Role-Based Technical Candidate Screening
        </h1>
        <p className="text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
          Dynamic interview questions generated and evaluated against foundational textbook literature 
          (Andriy Burkov's <em className="text-slate-300">The Hundred-Page ML Book</em> &amp; Systems Engineering Handbooks).
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold">Processing Notice:</strong> {error}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Role & File Upload */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            {/* Step 1: Target Role Selector */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                1. Select Target Engineering Role
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                {roles.map((r) => {
                  const isSelected = selectedRole === r.id;
                  return (
                    <button
                      key={r.id}
                      type="button"
                      onClick={() => setSelectedRole(r.id)}
                      className={`text-left p-3 rounded-xl border text-sm transition-all ${
                        isSelected
                          ? 'border-emerald-500 bg-emerald-500/10 text-white ring-2 ring-emerald-500/20'
                          : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                      }`}
                    >
                      <div className="font-semibold text-slate-100 flex items-center justify-between">
                        <span>{r.title}</span>
                        {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                        {r.description}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Step 2: Drag & Drop Zone */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                2. Upload Candidate Resume (PDF / Plain Text)
              </label>
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  isDragging
                    ? 'border-emerald-400 bg-emerald-500/5'
                    : selectedFile
                    ? 'border-emerald-500/60 bg-slate-950/80'
                    : 'border-slate-700 bg-slate-950/40 hover:border-slate-600 hover:bg-slate-950/60'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.doc,.docx"
                  className="hidden"
                  onChange={handleFileChange}
                />

                {selectedFile ? (
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                      <FileText className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-100">{selectedFile.name}</p>
                      <p className="text-xs text-slate-400">
                        {(selectedFile.size / 1024).toFixed(1)} KB &bull; Ready to parse
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedFile(null);
                      }}
                      className="text-xs text-red-400 hover:underline pt-1"
                    >
                      Remove file
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center space-y-3">
                    <div className="w-12 h-12 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center">
                      <Upload className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-200">
                        Drag and drop your resume file here, or <span className="text-emerald-400 underline">browse</span>
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        Supports PDF and UTF-8 plain text resumes
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Submit Action */}
            <button
              onClick={handleSubmit}
              disabled={!selectedFile || isLoading}
              className={`w-full py-3.5 px-5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
                !selectedFile || isLoading
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 active:scale-[0.99]'
              }`}
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Parsing Resume &amp; Grounding Corpus...</span>
                </>
              ) : (
                <>
                  <span>Begin Technical Screening</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Pre-loaded Demo Resumes */}
        <div className="space-y-4">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
              <Sparkles className="w-4 h-4" />
              <span>Instant Test Resumes</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Don't have a PDF ready? Select a calibrated sample profile to immediately test the end-to-end RAG pipeline:
            </p>

            <div className="space-y-2.5">
              {sampleResumes.map((sample) => (
                <button
                  key={sample.id}
                  onClick={() => onSelectSample(sample.id, sample.role)}
                  disabled={isLoading}
                  className="w-full text-left p-3.5 rounded-xl border border-slate-800 bg-slate-950/70 hover:border-emerald-500/50 hover:bg-slate-900 transition group"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-xs text-slate-200 group-hover:text-emerald-400">
                      {sample.name}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      {sample.role}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                    {sample.summary}
                  </p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {sample.skills.slice(0, 3).map((s) => (
                      <span key={s} className="text-[9px] px-1.5 py-0.2 rounded bg-slate-900 text-slate-300 border border-slate-800">
                        {s}
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>

            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
              <span>Grounds each question in verified textbook definitions.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
