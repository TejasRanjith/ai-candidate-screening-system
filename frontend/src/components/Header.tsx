import React from 'react';
import { Cpu, BookOpen, RefreshCw } from 'lucide-react';

interface HeaderProps {
  onReset?: () => void;
  activeRole?: string;
  step?: number;
}

export const Header: React.FC<HeaderProps> = ({ onReset, activeRole, step }) => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-inner">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-100 tracking-tight text-base sm:text-lg">
                RoleScan AI
              </span>
              <span className="px-2 py-0.5 text-xs font-mono rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                RAG Grounded
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Role-Based Adaptive Technical Screening Engine
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {activeRole && (
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300">
              <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
              <span>Target: <strong className="text-slate-100">{activeRole}</strong></span>
            </div>
          )}

          {step && step > 1 && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition"
              title="Start a new interview"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>New Screen</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
