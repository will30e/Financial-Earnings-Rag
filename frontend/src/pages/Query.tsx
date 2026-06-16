import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Search, Loader2, ChevronDown } from 'lucide-react'
import QueryResult from '../components/QueryResult'
import { runQuery, fetchCompanies, triggerIngestion, fetchJobs } from '../lib/api'
import type { QueryResponse } from '../lib/types'

const EXAMPLE_QUERIES = [
  'What was Apple\'s revenue growth in Q4 2024?',
  'Which technology companies beat earnings estimates in 2024?',
  'Compare NVIDIA and AMD EPS performance in Q3 2024',
  'What guidance did Microsoft provide for the upcoming quarter?',
  'Which companies in the financial sector showed the highest revenue growth?',
]

export default function Query() {
  const [queryText, setQueryText] = useState('')
  const [ticker, setTicker] = useState('')
  const [year, setYear] = useState<string>('')
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [history, setHistory] = useState<QueryResponse[]>([])

  const { data: companies = [] } = useQuery({
    queryKey: ['companies'],
    queryFn: () => fetchCompanies(),
  })

  const { data: jobs = [] } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 3_000,
  })

  const isIngesting = jobs.some((j) => j.status === 'running' || j.status === 'pending')
  const hasIndexedData = jobs.some((j) => j.status === 'completed' && j.chunks_indexed > 0)

  const ingest = useMutation({
    mutationFn: () => triggerIngestion(),
  })

  const query = useMutation({
    mutationFn: () =>
      runQuery({
        query: queryText,
        ticker: ticker || undefined,
        fiscal_year: year ? parseInt(year) : undefined,
        top_k: 5,
      }),
    onSuccess: (data) => {
      setResult(data)
      setHistory((prev) => [data, ...prev].slice(0, 5))
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!queryText.trim()) return
    query.mutate()
  }

  return (
    <div className="p-6 max-w-4xl space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">RAG Query</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Ask questions about earnings data across 57 companies using semantic search + LLM generation
        </p>
      </div>

      {/* Pipeline warning */}
      {!hasIndexedData && (
        <div className="card border-yellow-500/20 bg-yellow-500/5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-yellow-400">Vector index is empty</p>
              <p className="text-xs text-slate-500 mt-0.5">Run the ingestion pipeline first to index earnings data.</p>
            </div>
            <button
              className="btn-primary text-xs py-1.5"
              onClick={() => ingest.mutate()}
              disabled={isIngesting}
            >
              {isIngesting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
              {isIngesting ? 'Indexing…' : 'Run Ingestion'}
            </button>
          </div>
        </div>
      )}

      {/* Query form */}
      <div className="card space-y-3">
        <form onSubmit={handleSubmit} className="space-y-3">
          <textarea
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="Ask anything about earnings reports…"
            rows={3}
            className="w-full px-4 py-3 bg-surface-DEFAULT border border-surface-border rounded-lg text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-accent resize-none"
          />
          <div className="flex items-center gap-2">
            <select
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="px-3 py-2 bg-surface-DEFAULT border border-surface-border rounded-lg text-sm text-slate-300 focus:outline-none focus:border-accent"
            >
              <option value="">All companies</option>
              {companies.map((c) => (
                <option key={c.ticker} value={c.ticker}>{c.ticker} — {c.name}</option>
              ))}
            </select>
            <select
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="px-3 py-2 bg-surface-DEFAULT border border-surface-border rounded-lg text-sm text-slate-300 focus:outline-none focus:border-accent"
            >
              <option value="">All years</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
            </select>
            <button
              type="submit"
              className="btn-primary ml-auto"
              disabled={query.isPending || !queryText.trim()}
            >
              {query.isPending
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Searching…</>
                : <><Search className="w-4 h-4" /> Search</>
              }
            </button>
          </div>
        </form>

        {/* Example queries */}
        <div>
          <p className="text-xs text-slate-600 mb-2">Example queries:</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map((q) => (
              <button
                key={q}
                onClick={() => setQueryText(q)}
                className="text-xs px-2.5 py-1 bg-surface-DEFAULT border border-surface-border rounded-md text-slate-400 hover:text-slate-200 hover:border-accent/40 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error */}
      {query.isError && (
        <div className="card border-red-500/20 bg-red-500/5">
          <p className="text-sm text-red-400">Query failed: {String(query.error)}</p>
        </div>
      )}

      {/* Result */}
      {result && <QueryResult result={result} />}

      {/* History */}
      {history.length > 1 && (
        <details className="card">
          <summary className="text-sm font-medium text-slate-400 cursor-pointer flex items-center gap-2">
            <ChevronDown className="w-4 h-4" />
            Recent queries ({history.length - 1} more)
          </summary>
          <div className="mt-3 space-y-2">
            {history.slice(1).map((h, i) => (
              <button
                key={i}
                onClick={() => { setQueryText(h.query); setResult(h) }}
                className="w-full text-left px-3 py-2 rounded-lg bg-surface-DEFAULT border border-surface-border hover:border-accent/40 transition-colors"
              >
                <p className="text-xs text-slate-400 truncate">{h.query}</p>
                <p className="text-xs text-slate-600 mt-0.5">{h.latency_ms.toFixed(0)}ms · {h.sources.length} sources</p>
              </button>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
