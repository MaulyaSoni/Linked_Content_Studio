// frontend/src/components/GenerationProgress.tsx

import React from 'react';

interface GenerationProgressProps {
  step: string;
  message: string;
}

export function GenerationProgress({ step, message }: GenerationProgressProps) {
  const steps = ["analyzing", "researching", "drafting", "critiquing", "polishing"];
  const current = steps.indexOf(step);

  return (
    <div className="space-y-4 p-6 rounded-xl border bg-card text-card-foreground shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-primary">{message}</p>
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Step {Math.max(0, current + 1)} of {steps.length}
        </span>
      </div>
      
      <div className="flex gap-2">
        {steps.map((s, i) => (
          <div
            key={s}
            className={`h-2 flex-1 rounded-full transition-all duration-700 ease-in-out ${
              i <= current 
                ? "bg-primary shadow-[0_0_8px_rgba(var(--primary),0.4)]" 
                : "bg-muted"
            } ${i === current ? "animate-pulse" : ""}`}
          />
        ))}
      </div>
      
      <div className="flex justify-between px-1">
        {steps.map((s, i) => (
          <div 
            key={s} 
            className={`text-[10px] font-medium capitalize ${
              i <= current ? "text-primary" : "text-muted-foreground"
            }`}
          >
            {s}
          </div>
        ))}
      </div>
    </div>
  );
}
