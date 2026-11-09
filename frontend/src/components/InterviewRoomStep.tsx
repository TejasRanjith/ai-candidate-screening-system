import React, { useState, useEffect, useRef } from 'react';
import {
  BookOpen,
  Send,
  Sparkles,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  Code,
  CornerDownLeft
} from 'lucide-react';
import { TurnQuestionResponse, AnswerEvaluationResponse } from '../types';

interface InterviewRoomStepProps {
  question: TurnQuestionResponse;
  onSubmitAnswer: (answer: string) => Promise<AnswerEvaluationResponse>;
  onNextQuestion: () => Promise<void>;
  onViewReport: () => Promise<void>;
  isSubmitting: boolean;
  activeFeedback: AnswerEvaluationResponse | null;
}

export const InterviewRoomStep: React.FC<InterviewRoomStepProps> = ({
  question,
  onSubmitAnswer,
  onNextQuestion,
  onViewReport,
  isSubmitting,
  activeFeedback
}) => {
  const [answerText, setAnswerText] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Focus textarea when question changes
  useEffect(() => {
    if (!activeFeedback) {
      setAnswerText('');
      setTimeout(() => textareaRef.current?.focus(), 150);
    }
  }, [question.turn_index, activeFeedback]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (answerText.trim().length >= 5 && !isSubmitting) {
      await onSubmitAnswer(answerText.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  const wordCount = answerText.trim() ? answerText.trim().split(/\s+/).length : 0;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      {/* Top Turn Header & Badges */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              QUESTION {question.turn_index} OF {question.total_turns}
            </span>
            <span className="text-xs text-slate-400">&bull;</span>
            <span className="text-xs text-slate-300 font-medium">
              Targeted Skill: <strong className="text-slate-100">{question.targeted_skill}</strong>
            </span>
          </div>
          <h2 className="text-lg sm:text-xl font-bold text-slate-100 mt-1">
            {question.source_topic}
          </h2>
        </div>

        {/* Cited Concept Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <BookOpen className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
          <span className="font-mono text-[11px] truncate max-w-[260px]" title={question.cited_concept}>
            {question.cited_concept}
          </span>
        </div>
      </div>

      {/* Main Question Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-7 shadow-xl space-y-5">
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
            <Sparkles className="w-4 h-4" />
            <span>Scenario &amp; Theoretical Problem</span>
          </div>
          <p className="text-sm sm:text-base text-slate-100 leading-relaxed font-normal">
            {question.question_text}
          </p>
        </div>

        {/* Optional Grounded Context Preview Collapsible */}
        {question.retrieved_context_preview && (
          <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs text-slate-400">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5 mb-1">
              <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
              Retrieved Ground-Truth Reference Excerpt:
            </span>
            <p className="italic font-mono text-[11px] text-slate-400 leading-relaxed">
              "{question.retrieved_context_preview}"
            </p>
          </div>
        )}
      </div>

      {/* Turn Evaluation Feedback Overlay / Banner if active */}
      {activeFeedback ? (
        <div className="bg-slate-900/95 border border-emerald-500/40 rounded-2xl p-6 shadow-2xl space-y-5 animate-slideUp">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div
                className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg ${
                  activeFeedback.score >= 7.5
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : activeFeedback.score >= 5.0
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}
              >
                {activeFeedback.score.toFixed(1)}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-100 text-base">Turn {activeFeedback.turn_index} Evaluation</h4>
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    Accuracy: {activeFeedback.technical_accuracy}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">Scored against ground-truth textbook concepts</p>
              </div>
            </div>

            <span className="text-xs font-mono text-slate-400">
              Turn {activeFeedback.turn_index} of {activeFeedback.total_turns}
            </span>
          </div>

          <div className="space-y-3">
            {/* Constructive feedback */}
            <div className="text-xs sm:text-sm text-slate-200 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <p className="font-medium">{activeFeedback.constructive_feedback}</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              {/* Strengths */}
              <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-1.5">
                <span className="font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Recognized Strengths
                </span>
                <ul className="space-y-1 text-slate-300">
                  {activeFeedback.strengths.map((s, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-emerald-500 mt-0.5">&bull;</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Missing points */}
              <div className="p-3.5 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-1.5">
                <span className="font-semibold text-amber-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" /> Conceptual Gaps
                </span>
                <ul className="space-y-1 text-slate-300">
                  {activeFeedback.missing_points.map((m, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-amber-500 mt-0.5">&bull;</span>
                      <span>{m}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Model answer */}
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-400">
              <span className="font-semibold text-slate-300 flex items-center gap-1.5 mb-1">
                <Lightbulb className="w-3.5 h-3.5 text-yellow-400" /> Textbook Reference Summary:
              </span>
              <p className="italic text-slate-300">{activeFeedback.model_answer_summary}</p>
            </div>
          </div>

          <div className="pt-2">
            {activeFeedback.is_completed ? (
              <button
                onClick={onViewReport}
                className="w-full py-3.5 px-6 rounded-xl font-semibold text-sm bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition"
              >
                <span>Complete Interview &amp; View Comprehensive Report</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={onNextQuestion}
                className="w-full py-3.5 px-6 rounded-xl font-semibold text-sm bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition"
              >
                <span>Proceed to Question {activeFeedback.turn_index + 1}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Answer Input Area */
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
              <Code className="w-4 h-4 text-emerald-400" />
              <span>Your Response &amp; Architectural Reasoning</span>
            </label>
            <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
              <span>{wordCount} words</span>
              <span className="hidden sm:inline text-slate-600">|</span>
              <span className="hidden sm:flex items-center gap-1 text-[11px] text-slate-500">
                <CornerDownLeft className="w-3 h-3" /> Press Ctrl+Enter to submit
              </span>
            </div>
          </div>

          <textarea
            ref={textareaRef}
            rows={7}
            value={answerText}
            onChange={(e) => setAnswerText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSubmitting}
            placeholder="Structure your answer clearly. Detail the theoretical mechanics, parameter choices, and trade-offs. You can provide code snippets or pseudocode..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 font-mono transition resize-y leading-relaxed"
          />

          <div className="flex items-center justify-between pt-2">
            <div className="text-xs text-slate-500 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
              <span>Evaluated against ground truth: conceptual precision matters more than length.</span>
            </div>

            <button
              onClick={() => handleSubmit()}
              disabled={answerText.trim().length < 5 || isSubmitting}
              className={`py-3 px-6 rounded-xl font-semibold text-sm flex items-center gap-2 transition shadow-lg ${
                answerText.trim().length < 5 || isSubmitting
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20 active:scale-[0.99]'
              }`}
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Evaluating against Corpus...</span>
                </>
              ) : (
                <>
                  <span>Submit Answer</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
