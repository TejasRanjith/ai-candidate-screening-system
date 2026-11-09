import React from 'react';
import { FileUp, UserCheck, MessageSquareCode, Award } from 'lucide-react';

interface StepperProps {
  currentStep: number;
}

const steps = [
  { id: 1, label: 'Resume & Role', icon: FileUp },
  { id: 2, label: 'Candidate Profile', icon: UserCheck },
  { id: 3, label: 'Adaptive Screen', icon: MessageSquareCode },
  { id: 4, label: 'Final Report', icon: Award },
];

export const Stepper: React.FC<StepperProps> = ({ currentStep }) => {
  return (
    <nav aria-label="Progress" className="w-full max-w-4xl mx-auto px-4 py-4">
      <ol className="flex items-center justify-between relative">
        <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-0.5 bg-slate-800 -z-0" />
        
        {steps.map((step) => {
          const Icon = step.icon;
          const isDone = currentStep > step.id;
          const isCurrent = currentStep === step.id;

          return (
            <li key={step.id} className="relative z-10 flex flex-col items-center">
              <div
                className={`w-9 h-9 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center font-medium transition-all ${
                  isDone
                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                    : isCurrent
                    ? 'bg-slate-900 border-2 border-emerald-500 text-emerald-400 ring-4 ring-emerald-500/10'
                    : 'bg-slate-900 border border-slate-700 text-slate-500'
                }`}
              >
                <Icon className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <span
                className={`mt-2 text-[11px] sm:text-xs font-medium tracking-tight ${
                  isCurrent
                    ? 'text-emerald-400 font-semibold'
                    : isDone
                    ? 'text-slate-300'
                    : 'text-slate-500'
                }`}
              >
                {step.label}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
