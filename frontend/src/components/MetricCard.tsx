import clsx from 'clsx'

interface MetricCardProps {
  label: string
  value: string | number
  sub?: string
  trend?: 'up' | 'down' | 'neutral'
  icon?: React.ReactNode
  mono?: boolean
}

export default function MetricCard({ label, value, sub, trend, icon, mono }: MetricCardProps) {
  return (
    <div className="card flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</span>
        {icon && <span className="text-slate-600">{icon}</span>}
      </div>
      <div>
        <p
          className={clsx(
            'text-2xl font-bold text-white',
            mono && 'font-mono',
          )}
        >
          {value}
        </p>
        {sub && (
          <p
            className={clsx(
              'text-xs mt-1',
              trend === 'up' && 'text-green-400',
              trend === 'down' && 'text-red-400',
              trend === 'neutral' && 'text-slate-500',
              !trend && 'text-slate-500',
            )}
          >
            {sub}
          </p>
        )}
      </div>
    </div>
  )
}
