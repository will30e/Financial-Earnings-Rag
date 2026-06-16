import { TrendingUp, TrendingDown } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { EarningsReport } from '../lib/types'

interface CompanyCardProps {
  report: EarningsReport
}

export default function CompanyCard({ report }: CompanyCardProps) {
  const up = report.revenue_yoy >= 0
  const epsUp = report.eps_yoy >= 0

  return (
    <Link
      to={`/companies/${report.ticker}`}
      className="card hover:border-accent/40 hover:bg-surface-hover transition-all block"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="text-xs font-mono font-semibold text-accent">{report.ticker}</span>
          <p className="text-sm font-medium text-white mt-0.5 leading-tight">{report.company_name}</p>
        </div>
        <span className="badge-blue text-[10px]">{report.sector}</span>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-xs text-slate-500 mb-0.5">Revenue</p>
          <p className="font-mono font-medium text-white">${report.revenue.toFixed(1)}B</p>
          <div className={`flex items-center gap-0.5 text-xs mt-0.5 ${up ? 'text-green-400' : 'text-red-400'}`}>
            {up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {report.revenue_yoy > 0 ? '+' : ''}{report.revenue_yoy.toFixed(1)}% YoY
          </div>
        </div>
        <div>
          <p className="text-xs text-slate-500 mb-0.5">EPS</p>
          <p className="font-mono font-medium text-white">${report.eps.toFixed(2)}</p>
          <div className={`flex items-center gap-0.5 text-xs mt-0.5 ${epsUp ? 'text-green-400' : 'text-red-400'}`}>
            {epsUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {report.eps_yoy > 0 ? '+' : ''}{report.eps_yoy.toFixed(1)}% YoY
          </div>
        </div>
      </div>

      {/* Beat indicator */}
      <div className="mt-3 pt-3 border-t border-surface-border flex items-center justify-between">
        <span className="text-xs text-slate-500">Q{report.fiscal_quarter} {report.fiscal_year}</span>
        <span className={report.beat_estimate ? 'badge-green' : 'badge-red'}>
          {report.beat_estimate ? '✓ Beat' : '✗ Missed'}
        </span>
      </div>
    </Link>
  )
}
