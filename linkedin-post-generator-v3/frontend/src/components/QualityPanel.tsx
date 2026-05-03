// components/QualityPanel.tsx

interface QualityBadgeProps {
  score: number
  modeUsed: string
  hasHistory: boolean
}

export default function QualityPanel({ score, modeUsed, hasHistory }: QualityBadgeProps) {
  const color =
    score >= 80 ? "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800/50" :
    score >= 60 ? "text-amber-600 bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800/50" :
                  "text-red-600 bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800/50"

  return (
    <div className="mt-4 flex flex-wrap gap-2 items-center">
      {/* Score */}
      <span className={`text-xs font-bold px-3 py-1 rounded-full border ${color}`}>
        Quality {score}/100
      </span>

      {/* Personalization signal */}
      {modeUsed === "langgraph_orchestrated" && (
        <span className="text-xs font-bold px-3 py-1 rounded-full border
                         text-blue-600 bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800/50">
          ✦ AI-orchestrated · {hasHistory ? "Style-matched" : "Default style"}
        </span>
      )}

      {/* New user nudge */}
      {!hasHistory && modeUsed === "langgraph_orchestrated" && (
        <span className="text-xs text-muted-foreground ml-1">
          Generate more posts to improve personalization
        </span>
      )}
    </div>
  )
}
