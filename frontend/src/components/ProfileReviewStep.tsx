import React from 'react';
import { Briefcase, Award, CheckCircle2, ArrowRight, Layers, FileCode, Sparkles } from 'lucide-react';
import { SessionStartResponse } from '../types';

interface ProfileReviewStepProps {
  session: SessionStartResponse;
  onProceed: () => void;
  isLoading: boolean;
}

export const ProfileReviewStep: React.FC<ProfileReviewStepProps> = ({
  session,
  onProceed,
  isLoading
}) => {
  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="text-center space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Resume Successfully Processed</span>
        </div>
        <h2 className="text-2xl font-bold text-slate-100">Parsed Profile Confirmation</h2>
        <p className="text-sm text-slate-400">
          Verify the extracted entity skills and domain experience before entering the adaptive interview room.
        </p>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        {/* Candidate Overview Card */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white flex items-center justify-center font-bold text-xl shadow-lg shadow-emerald-900/40">
              {session.candidate_name ? session.candidate_name[0] : 'C'}
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-100">{session.candidate_name}</h3>
              <div className="flex flex-wrap items-center gap-2 mt-1">
                <span className="flex items-center gap-1 text-xs text-slate-300">
                  <Briefcase className="w-3.5 h-3.5 text-emerald-400" />
                  {session.target_role}
                </span>
                <span className="text-slate-600">&bull;</span>
                <span className="flex items-center gap-1 text-xs text-emerald-400 font-medium">
                  <Award className="w-3.5 h-3.5" />
                  {session.experience_level}
                </span>
              </div>
            </div>
          </div>

          <div className="px-3.5 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs font-mono text-slate-300">
            Session: <span className="text-slate-100">{session.session_id.slice(0, 8)}...</span>
          </div>
        </div>

        {/* Executive Summary */}
        {session.raw_summary && (
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs sm:text-sm text-slate-300 leading-relaxed">
            <span className="font-semibold text-slate-200">Profile Summary: </span>
            {session.raw_summary}
          </div>
        )}

        {/* Detected Skills */}
        <div className="space-y-2.5">
          <label className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            <FileCode className="w-3.5 h-3.5 text-emerald-400" />
            <span>Extracted Technical Competencies ({session.parsed_skills.length})</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {session.parsed_skills.map((skill) => (
              <span
                key={skill}
                className="px-3 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs font-mono border border-slate-700/60 flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Domain Exposure */}
        <div className="space-y-2.5">
          <label className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            <Layers className="w-3.5 h-3.5 text-teal-400" />
            <span>Domain Exposure &amp; Architecture Areas</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {session.domain_exposure.map((domain) => (
              <span
                key={domain}
                className="px-3 py-1 rounded-lg bg-teal-500/10 text-teal-300 text-xs border border-teal-500/20"
              >
                {domain}
              </span>
            ))}
          </div>
        </div>

        {/* Key Highlights */}
        {session.project_highlights && session.project_highlights.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Anchored Past Projects &amp; Experience
            </label>
            <ul className="space-y-2">
              {session.project_highlights.map((item, idx) => (
                <li
                  key={idx}
                  className="text-xs text-slate-300 p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 flex items-start gap-2"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Confirmation Action */}
        <div className="pt-4 border-t border-slate-800">
          <button
            onClick={onProceed}
            disabled={isLoading}
            className="w-full py-3.5 px-6 rounded-xl font-semibold text-sm bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition active:scale-[0.99]"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Preparing Grounded Questions...</span>
              </>
            ) : (
              <>
                <span>Enter Technical Interview Room ({session.total_turns} Questions)</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
