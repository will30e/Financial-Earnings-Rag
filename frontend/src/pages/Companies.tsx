import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Search } from 'lucide-react'
import CompanyCard from '../components/CompanyCard'
import EarningsTable from '../components/EarningsTable'
import { fetchLatestEarnings, fetchEarnings, fetchSectors } from '../lib/api'

export default function Companies() {
  const { ticker } = useParams<{ ticker?: string }>()
  const navigate = useNavigate()

  if (ticker) return <CompanyDetail ticker={ticker} onBack={() => navigate('/companies')} />
  return <CompanyList />
}

function CompanyList() {
  const [search, setSearch] = useState('')
  const [sector, setSector] = useState<string>('')

  const { data: sectors = [] } = useQuery({
    queryKey: ['sectors'],
    queryFn: fetchSectors,
  })

  const { data: earnings = [], isLoading } = useQuery({
    queryKey: ['latest-earnings', sector],
    queryFn: () => fetchLatestEarnings(57, sector || undefined),
  })

  const filtered = earnings.filter(
    (r) =>
      r.ticker.toLowerCase().includes(search.toLowerCase()) ||
      r.company_name.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Companies</h1>
        <p className="text-sm text-slate-500 mt-0.5">Q4 2024 earnings for all tracked companies</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search ticker or name…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-surface-card border border-surface-border rounded-lg text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-accent"
          />
        </div>
        <select
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          className="px-3 py-2 bg-surface-card border border-surface-border rounded-lg text-sm text-slate-300 focus:outline-none focus:border-accent"
        >
          <option value="">All Sectors</option>
          {sectors.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <span className="text-xs text-slate-500">{filtered.length} companies</span>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="card animate-pulse h-36 bg-surface-hover" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((r) => (
            <CompanyCard key={r.ticker} report={r} />
          ))}
        </div>
      )}
    </div>
  )
}

function CompanyDetail({ ticker, onBack }: { ticker: string; onBack: () => void }) {
  const { data: reports = [], isLoading } = useQuery({
    queryKey: ['earnings', ticker],
    queryFn: () => fetchEarnings(ticker),
  })

  const latest = reports[0]

  return (
    <div className="p-6 space-y-5">
      <button onClick={onBack} className="btn-ghost -ml-1">
        <ArrowLeft className="w-4 h-4" />
        Back to Companies
      </button>

      {isLoading ? (
        <div className="card animate-pulse h-48" />
      ) : latest ? (
        <>
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono font-bold text-accent text-lg">{ticker.toUpperCase()}</span>
                  <span className="badge-blue">{latest.sector}</span>
                </div>
                <h1 className="text-xl font-bold text-white">{latest.company_name}</h1>
              </div>
              <span className={latest.beat_estimate ? 'badge-green' : 'badge-red'}>
                Q{latest.fiscal_quarter} {latest.fiscal_year}: {latest.beat_estimate ? 'Beat' : 'Miss'}
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">{latest.management_commentary}</p>
          </div>

          <div className="card">
            <h2 className="text-sm font-semibold text-white mb-4">Historical Earnings (2023–2024)</h2>
            <EarningsTable reports={reports} />
          </div>
        </>
      ) : (
        <p className="text-slate-500">No data found for {ticker}</p>
      )}
    </div>
  )
}
