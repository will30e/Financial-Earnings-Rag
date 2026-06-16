export interface Company {
  ticker: string
  name: string
  sector: string
  description?: string
}

export interface EarningsReport {
  ticker: string
  company_name: string
  sector: string
  fiscal_quarter: string
  fiscal_year: number
  report_date: string
  revenue: number
  revenue_yoy: number
  eps: number
  eps_yoy: number
  net_income: number
  operating_cash_flow: number
  guidance_revenue: number
  guidance_eps: number
  beat_estimate: boolean
  summary: string
  management_commentary: string
}

export interface SourceChunk {
  ticker: string
  company_name: string
  fiscal_quarter: string
  fiscal_year: number
  text: string
  relevance_score: number
}

export interface QueryRequest {
  query: string
  ticker?: string
  fiscal_year?: number
  top_k?: number
}

export interface QueryResponse {
  query: string
  answer: string
  sources: SourceChunk[]
  latency_ms: number
  retrieval_latency_ms: number
  generation_latency_ms: number
}

export interface HealthStatus {
  status: string
  version: string
  database: string
  vector_store: string
  companies_tracked: number
  reports_indexed: number
  uptime_seconds: number
}

export interface IngestionJob {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  ticker?: string
  started_at: string
  completed_at?: string
  records_processed: number
  chunks_indexed: number
  error?: string
}
