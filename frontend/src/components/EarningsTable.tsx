import { TrendingUp, TrendingDown } from 'lucide-react'
import type { EarningsReport } from '../lib/types'

interface EarningsTableProps {
  reports: EarningsReport[]
}

function Trend({ value }: { value: number }) {
  const up = value >= 0
  return (
    <span className={`flex items-center gap-0.5 text-xs ${up ? 'text-green-400' : 'text-red-400'}`}>
      {up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
      {value > 0 ? '+' : ''}{value.toFixed(1)}%
    </span>
  )
}

export default function EarningsTable({ reports }: EarningsTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-surface-border">
            {['Period', 'Revenue', 'YoY', 'EPS', 'YoY', 'Net Income', 'OCF', 'Result'].map((h) => (
              <th key={h} className="text-left text-xs text-slate-500 uppercase tracking-wider pb-2 pr-4 font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-border">
          {reports.map((r) => (
            <tr key={`${r.fiscal_quarter}-${r.fiscal_year}`} className="hover:bg-surface-hover transition-colors">
              <td className="py-2.5 pr-4 font-mono text-xs text-slate-400">Q{r.fiscal_quarter} {r.fiscal_year}</td>
              <td className="py-2.5 pr-4 font-mono text-white">${r.revenue.toFixed(1)}B</td>
              <td className="py-2.5 pr-4"><Trend value={r.revenue_yoy} /></td>
              <td className="py-2.5 pr-4 font-mono text-white">${r.eps.toFixed(2)}</td>
              <td className="py-2.5 pr-4"><Trend value={r.eps_yoy} /></td>
              <td className="py-2.5 pr-4 font-mono text-slate-300">${r.net_income.toFixed(1)}B</td>
              <td className="py-2.5 pr-4 font-mono text-slate-300">${r.operating_cash_flow.toFixed(1)}B</td>
              <td className="py-2.5">
                <span className={r.beat_estimate ? 'badge-green' : 'badge-red'}>
                  {r.beat_estimate ? '✓ Beat' : '✗ Miss'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
