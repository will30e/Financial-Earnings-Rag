import { Clock, Database, Zap } from 'lucide-react'
import type { QueryResponse } from '../lib/types'

interface QueryResultProps {
  result: QueryResponse
}

export default function QueryResult({ result }: QueryResultProps) {
  return (
    <div className="space-y-4">
      {/* Answer */}
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-accent" />
          <h3 className="text-sm font-semibold text-white">Answer</h3>
          <div className="ml-auto flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {result.latency_ms.toFixed(0)}ms total
            </span>
            <span>retrieval {result.retrieval_latency_ms.toFixed(0)}ms</span>
          </div>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{result.answer}</p>
      </div>

      {/* Sources */}
      {result.sources.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-slate-500" />
            <h3 className="text-sm font-semibold text-white">Sources</h3>
            <span className="badge-blue ml-auto">{result.sources.length} chunks</span>
          </div>
          <div className="space-y-2">
            {result.sources.map((src, i) => (
              <div key={i} className="bg-surface-DEFAULT border border-surface-border rounded-lg p-3">
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-accent">{src.ticker}</span>
                    <span className="text-xs text-slate-500">{src.company_name}</span>
                    <span className="badge-blue text-[10px]">Q{src.fiscal_quarter} {src.fiscal_year}</span>
                  </div>
                  <span className="text-xs text-slate-500 font-mono">
                    {(src.relevance_score * 100).toFixed(1)}% match
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">{src.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
