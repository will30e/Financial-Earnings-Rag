import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Building2, Database, Activity, Zap, Play, RefreshCw } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import MetricCard from '../components/MetricCard'
import PipelineStatus from '../components/PipelineStatus'
import { fetchHealth, fetchLatestEarnings, triggerIngestion, fetchJobs } from '../lib/api'

export default function Dashboard() {
  const qc = useQueryClient()

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 15_000,
  })

  const { data: earnings = [] } = useQuery({
    queryKey: ['latest-earnings'],
    queryFn: () => fetchLatestEarnings(57),
  })

  const { data: jobs = [] } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 3_000,
  })

  const ingest = useMutation({
    mutationFn: () => triggerIngestion(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['jobs'] })
      qc.invalidateQueries({ queryKey: ['health'] })
    },
  })

  // Aggregate by sector
  const sectorMap: Record<string, { count: number; beat: number }> = {}
  earnings.forEach((r) => {
    if (!sectorMap[r.sector]) sectorMap[r.sector] = { count: 0, beat: 0 }
    sectorMap[r.sector].count++
    if (r.beat_estimate) sectorMap[r.sector].beat++
  })
  const sectorData = Object.entries(sectorMap).map(([sector, { count, beat }]) => ({
    sector: sector.length > 14 ? sector.slice(0, 13) + '…' : sector,
    fullSector: sector,
    beat,
    miss: count - beat,
  }))

  const beatRate = earnings.length
    ? Math.round((earnings.filter((r) => r.beat_estimate).length / earnings.length) * 100)
    : 0

  const avgRevYoY = earnings.length
    ? (earnings.reduce((s, r) => s + r.revenue_yoy, 0) / earnings.length).toFixed(1)
    : '—'

  const activeJobs = jobs.filter((j) => j.status === 'running').length

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Pipeline Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">Real-time earnings intelligence across 57 companies</p>
        </div>
        <div className="flex items-center gap-2">
          {health && (
            <span className="flex items-center gap-1.5 text-xs text-green-400">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              {health.status}
            </span>
          )}
          <button
            className="btn-primary"
            onClick={() => ingest.mutate()}
            disabled={ingest.isPending || activeJobs > 0}
          >
            {ingest.isPending || activeJobs > 0
              ? <><RefreshCw className="w-4 h-4 animate-spin" /> Ingesting…</>
              : <><Play className="w-4 h-4" /> Run Pipeline</>
            }
          </button>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Companies Tracked"
          value={health?.companies_tracked ?? 57}
          sub="S&P 500 large caps"
          trend="neutral"
          icon={<Building2 className="w-4 h-4" />}
        />
        <MetricCard
          label="Chunks Indexed"
          value={health?.reports_indexed.toLocaleString() ?? '—'}
          sub="In vector store"
          trend="neutral"
          icon={<Database className="w-4 h-4" />}
          mono
        />
        <MetricCard
          label="Beat Rate"
          value={`${beatRate}%`}
          sub={`${earnings.filter((r) => r.beat_estimate).length} of ${earnings.length} companies`}
          trend={beatRate > 70 ? 'up' : 'down'}
          icon={<Activity className="w-4 h-4" />}
        />
        <MetricCard
          label="Avg Revenue Growth"
          value={`${avgRevYoY}%`}
          sub="YoY across all companies"
          trend={Number(avgRevYoY) > 0 ? 'up' : 'down'}
          icon={<Zap className="w-4 h-4" />}
        />
      </div>

      {/* Charts + Pipeline status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Beat/Miss by sector */}
        <div className="card lg:col-span-2">
          <h2 className="text-sm font-semibold text-white mb-4">Earnings Performance by Sector</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={sectorData} barSize={14} barGap={2}>
              <XAxis
                dataKey="sector"
                tick={{ fill: '#64748b', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: '#161b27', border: '1px solid #1e2536', borderRadius: 8 }}
                labelStyle={{ color: '#e2e8f0', fontSize: 12 }}
                itemStyle={{ color: '#94a3b8', fontSize: 12 }}
              />
              <Bar dataKey="beat" name="Beat" stackId="a" fill="#22c55e" radius={[0, 0, 0, 0]} />
              <Bar dataKey="miss" name="Miss" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pipeline jobs */}
        <div>
          <h2 className="text-sm font-semibold text-white mb-4">Pipeline Jobs</h2>
          <PipelineStatus jobs={jobs.slice(0, 5)} />
        </div>
      </div>

      {/* Uptime strip */}
      {health && (
        <div className="card flex items-center gap-6 text-xs text-slate-500 font-mono">
          <span>uptime: {Math.floor(health.uptime_seconds / 60)}m {Math.floor(health.uptime_seconds % 60)}s</span>
          <span>db: <span className="text-green-400">{health.database}</span></span>
          <span>vector store: <span className="text-green-400">{health.vector_store}</span></span>
          <span>version: {health.version}</span>
        </div>
      )}
    </div>
  )
}
