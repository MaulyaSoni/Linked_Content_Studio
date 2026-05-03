import React from 'react';

interface Props {
  qualityScore: number;
  modeUsed: string;
}

export function PersonalizationBadges({ qualityScore, modeUsed }: Props) {
  return (
    <div className="flex items-center gap-3 mt-4 flex-wrap">
      {/* Quality score badge */}
      <span className={`
        px-3 py-1 rounded-full text-xs font-semibold
        ${qualityScore >= 80 ? 'bg-emerald-100 text-emerald-700' :
          qualityScore >= 60 ? 'bg-amber-100 text-amber-700' :
          'bg-red-100 text-red-700'}
      `}>
        Quality {qualityScore}/100
      </span>

      {/* Personalization badge */}
      {modeUsed === 'personalized_advanced' && (
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
          ✦ Style-matched to you
        </span>
      )}
    </div>
  )
}
