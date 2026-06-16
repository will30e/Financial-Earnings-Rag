import { CheckCircle, XCircle, Loader2, Clock } from 'lucide-react'
import type { IngestionJob } from '../lib/types'
import clsx from 'clsx'

const statusConfig = {
  pending: { icon: Clock, color: 'text-yellow-400', label: 'Pending' },
  running: { icon: Loader2, color: 'text-blue-400', label: 'Running', spin: true },
  completed: { icon: CheckCircle, color: 'text-green-400', label: 'Completed' },
  failed: { icon: XCircle, color: 'text-red-400', label: 'Failed' },
}

interface PipelineStatusProps {
  jobs: IngestionJob[]
}

export default function PipelineStatus({ jobs }: PipelineStatusProps) {
  if (jobs.length === 0) {
    return (
      <div className="card">
        <p className="text-sm text-slate-500 text-center py-4">No pipeline jobs yet. Run ingestion to index earnings data.</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {jobs.map((job) => {
        const cfg = statusConfig[job.status]
        const Icon = cfg.icon
        return (
          <div key={job.id} className="card">
            <div className="flex items-center gap-3">
              <Icon className={clsx('w-4 h-4 flex-shrink-0', cfg.color, 'spin' in cfg && cfg.spin && 'animate-spin')} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">
                    {job.ticker ? `Ingest ${job.ticker}` : 'Full ingestion (57 companies)'}
                  </span>
                  <span className={clsx('badge text-[10px]',
                    job.status === 'completed' ? 'badge-green' :
                    job.status === 'failed' ? 'badge-red' :
                    job.status === 'running' ? 'badge-blue' : 'badge-yellow'
                  )}>{cfg.label}</span>
                </div>
                <div className="flex items-center gap-4 mt-0.5">
                  <span className="text-xs text-slate-500 font-mono">{job.id.slice(0, 8)}</span>
                  {job.records_processed > 0 && (
                    <span className="text-xs text-slate-500">{job.records_processed} reports · {job.chunks_indexed} chunks</span>
                  )}
                  {job.error && (
                    <span className="text-xs text-red-400">{job.error}</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
