import axios from 'axios'
import type {
  Company,
  EarningsReport,
  HealthStatus,
  IngestionJob,
  QueryRequest,
  QueryResponse,
} from './types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30_000,
})

export async function fetchHealth(): Promise<HealthStatus> {
  const { data } = await axios.get('/health')
  return data
}

export async function fetchCompanies(sector?: string): Promise<Company[]> {
  const { data } = await api.get('/companies', { params: sector ? { sector } : {} })
  return data
}

export async function fetchCompany(ticker: string): Promise<Company> {
  const { data } = await api.get(`/companies/${ticker}`)
  return data
}

export async function fetchSectors(): Promise<string[]> {
  const { data } = await api.get('/sectors')
  return data
}

export async function fetchEarnings(
  ticker: string,
  year?: number,
  quarter?: string,
): Promise<EarningsReport[]> {
  const { data } = await api.get(`/earnings/${ticker}`, {
    params: { year, quarter },
  })
  return data
}

export async function fetchLatestEarnings(
  limit = 20,
  sector?: string,
): Promise<EarningsReport[]> {
  const { data } = await api.get('/earnings', { params: { limit, sector } })
  return data
}

export async function runQuery(request: QueryRequest): Promise<QueryResponse> {
  const { data } = await api.post('/query', request)
  return data
}

export async function triggerIngestion(ticker?: string): Promise<IngestionJob> {
  const { data } = await api.post('/pipeline/ingest', { ticker: ticker || null })
  return data
}

export async function fetchJobs(): Promise<IngestionJob[]> {
  const { data } = await api.get('/pipeline/jobs')
  return data
}

export async function fetchJob(jobId: string): Promise<IngestionJob> {
  const { data } = await api.get(`/pipeline/jobs/${jobId}`)
  return data
}
