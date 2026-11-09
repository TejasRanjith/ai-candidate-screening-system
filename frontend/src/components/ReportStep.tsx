import React, { useState } from 'react';
import {
  Award,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Download,
  Sparkles
} from 'lucide-react';
import { FinalReportResponse } from '../types';

interface ReportStepProps {
  report: FinalReportResponse;
  onReset: () => void;
}

export const ReportStep: React.FC<ReportStepProps> = ({ report, onReset }) => {
  const [expandedTurns, setExpandedTurns] = useState<Record<number, boolean>>({
    1: true // Expand first turn by default
  });

  const toggleTurn = (turnIndex: number) => {
    setExpandedTurns((prev) => ({
      ...prev,
      [turnIndex]: !prev[turnIndex]
    }));
  };

  const handleDownload = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Screening_Report_${report.candidate_name.replace(/\s+/g, '_')}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getScoreColor = (score: number) => {
    if (score >= 8.0) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 6.0) return 'text-teal-400 bg-teal-500/10 border-teal-500/30';
    if (score >= 4.5) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-red-400 bg-red-500/10 border-red-500/30';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Top Banner */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono mb-1">
          <Award className="w-3.5 h-3.5" />
          <span>Technical Assessment Complete</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-100">
          Executive Screening Report
        </h2>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Comprehensive diagnostic analysis based on grounded textbook evaluation and candidate responses.
        </p>
      </div>

      {/* Overall Score & Tier Hero Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
          {/* Left: Candidate & Role metadata */}
          <div className="space-y-3 text-center md:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-slate-800 text-slate-300 text-xs font-mono">
              <span>{report.target_role}</span>
              <span>&bull;</span>
              <span>{report.experience_level}</span>
            </div>
            <h3 className="text-2xl font-bold text-slate-100">{report.candidate_name}</h3>
            <p className="text-xs sm:text-sm text-slate-400 max-w-md leading-relaxed">
              {report.summary}
            </p>
            <div className="pt-1">
              <span className="text-xs px-3 py-1.5 rounded-xl font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Recommendation: {report.hiring_recommendation}
              </span>
            </div>
          </div>

          {/* Right: Big Score Gauge */}
          <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-950/80 border border-slate-800/80 min-w-[200px]">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Overall Rating
            </span>
            <div className="flex items-baseline gap-1">
              <span className="text-5xl font-black tracking-tight text-emerald-400">
                {report.overall_score.toFixed(1)}
              </span>
              <span className="text-slate-500 text-lg font-mono">/10</span>
            </div>
            <span className="mt-2 text-xs font-medium px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              {report.performance_tier}
            </span>
            <span className="text-[11px] text-slate-500 mt-2 font-mono">
              {report.completed_turns} / {report.total_turns} Turns Evaluated
            </span>
          </div>
        </div>
      </div>

      {/* Strengths & Improvements Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Verified Strengths */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>Key Demonstrated Strengths</span>
          </div>
          <ul className="space-y-2">
            {report.strengths.map((str, idx) => (
              <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Identified Areas for Improvement */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-amber-400">
            <AlertTriangle className="w-4 h-4" />
            <span>Areas for Theoretical Refinement</span>
          </div>
          <ul className="space-y-2">
            {report.areas_for_improvement.map((area, idx) => (
              <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                <span>{area}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Accordion: Detailed Turn Breakdown */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Question-by-Question Diagnostic Audit ({report.turns.length} Turns)
          </h3>
          <span className="text-xs text-slate-500">Traceable context &rarr; question &rarr; evaluation</span>
        </div>

        <div className="space-y-3">
          {report.turns.map((turn) => {
            const isExpanded = expandedTurns[turn.turn_index];
            const scoreClass = turn.score ? getScoreColor(turn.score) : 'text-slate-400 bg-slate-800 border-slate-700';

            return (
              <div
                key={turn.turn_index}
                className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden transition-all shadow-md"
              >
                {/* Header row */}
                <button
                  type="button"
                  onClick={() => toggleTurn(turn.turn_index)}
                  className="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-slate-850/50 transition gap-4"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      Q{turn.turn_index}
                    </span>
                    <div>
                      <h4 className="font-semibold text-sm text-slate-100">
                        {turn.source_topic}
                      </h4>
                      <p className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                        <span>Target: <strong>{turn.targeted_skill}</strong></span>
                        <span>&bull;</span>
                        <span className="truncate max-w-[280px] font-mono text-[11px] text-slate-400">
                          {turn.cited_concept}
                        </span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0">
                    {turn.score !== null && turn.score !== undefined && (
                      <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded-lg border ${scoreClass}`}>
                        {turn.score.toFixed(1)} / 10
                      </span>
                    )}
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </button>

                {/* Collapsible Details */}
                {isExpanded && (
                  <div className="p-4 sm:p-6 border-t border-slate-800/80 bg-slate-950/40 space-y-4 text-xs animate-fadeIn">
                    {/* Question text */}
                    <div className="space-y-1">
                      <span className="font-semibold text-emerald-400 uppercase tracking-wider text-[11px]">
                        Generated Technical Question:
                      </span>
                      <p className="text-slate-200 text-sm leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                        {turn.question_text}
                      </p>
                    </div>

                    {/* Candidate Answer */}
                    <div className="space-y-1">
                      <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">
                        Candidate Submitted Response:
                      </span>
                      <p className="text-slate-300 font-mono text-xs leading-relaxed bg-slate-950/90 p-3.5 rounded-xl border border-slate-800/80 whitespace-pre-wrap">
                        {turn.candidate_answer || "No response recorded."}
                      </p>
                    </div>

                    {/* Evaluator Analysis */}
                    {turn.constructive_feedback && (
                      <div className="space-y-1.5 p-3.5 rounded-xl bg-slate-900 border border-slate-800">
                        <span className="font-semibold text-emerald-400 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5" /> AI Evaluator Diagnostic Feedback:
                        </span>
                        <p className="text-slate-200 leading-relaxed">
                          {turn.constructive_feedback}
                        </p>
                      </div>
                    )}

                    {/* Ground truth reference summary */}
                    {turn.model_answer_summary && (
                      <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-400">
                        <span className="font-semibold text-slate-300 flex items-center gap-1.5 mb-1">
                          <BookOpen className="w-3.5 h-3.5 text-teal-400" /> Ground-Truth Textbook Concept ({turn.cited_concept}):
                        </span>
                        <p className="italic text-slate-300 font-mono text-[11px]">
                          {turn.model_answer_summary}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-6 border-t border-slate-800">
        <button
          onClick={handleDownload}
          className="w-full sm:w-auto px-5 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center justify-center gap-2 transition"
        >
          <Download className="w-4 h-4" />
          <span>Export Full JSON Report</span>
        </button>

        <button
          onClick={onReset}
          className="w-full sm:w-auto px-6 py-2.5 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Screen Another Candidate</span>
        </button>
      </div>
    </div>
  );
};
