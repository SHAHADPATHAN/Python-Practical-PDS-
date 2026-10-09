import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30_000,
})

// ─── Dataset ────────────────────────────────────────────────────────────────
export const fetchDatasetSummary  = () => api.get('/dataset/summary').then(r => r.data)
export const fetchLabelDist       = () => api.get('/dataset/labels').then(r => r.data)
export const fetchScannerBreakdown = () => api.get('/dataset/scanners').then(r => r.data)

// ─── EDA ────────────────────────────────────────────────────────────────────
export const fetchEdaSummary      = () => api.get('/eda/summary').then(r => r.data)
export const fetchHourlyActivity  = () => api.get('/eda/hourly').then(r => r.data)
export const fetchRequestsByHour  = () => api.get('/eda/requests-by-hour').then(r => r.data)
export const fetchTopIps          = () => api.get('/eda/top-ips').then(r => r.data)
export const fetchTopScannerIps   = () => api.get('/eda/top-scanner-ips').then(r => r.data)
export const fetchHeatmap         = () => api.get('/eda/heatmap').then(r => r.data)

// ─── IP Intelligence ────────────────────────────────────────────────────────
export const fetchIpList = (params: Record<string, any>) =>
  api.get('/ips', { params }).then(r => r.data)
export const fetchTopIpsFull = (n = 10) =>
  api.get('/ips/top', { params: { n } }).then(r => r.data)
export const fetchIpDetail = (ip: string) =>
  api.get(`/ips/${encodeURIComponent(ip)}`).then(r => r.data)

// ─── ML Model ────────────────────────────────────────────────────────────────
export const fetchModelInfo       = () => api.get('/model/info').then(r => r.data)
export const postModelPredict     = (features: Record<string, any>) =>
  api.post('/model/predict', { features }).then(r => r.data)

// ─── Records ─────────────────────────────────────────────────────────────────
export const fetchRecords = (params: Record<string, any>) =>
  api.get('/records', { params }).then(r => r.data)
export const fetchRecordColumns = () =>
  api.get('/records/columns').then(r => r.data)

// ─── Practicals & Reports ────────────────────────────────────────────────────
export const fetchPracticals  = () => api.get('/practicals').then(r => r.data)
export const fetchPractical   = (id: number) => api.get(`/practicals/${id}`).then(r => r.data)
export const fetchReports     = () => api.get('/reports').then(r => r.data)
export const fetchReport      = (key: string) => api.get(`/reports/${key}`).then(r => r.data)

// ─── Upload ──────────────────────────────────────────────────────────────────
export const uploadLog = (file: File, parserHint?: string) => {
  const form = new FormData()
  form.append('file', file)
  if (parserHint) form.append('parser_hint', parserHint)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120_000,
  }).then(r => r.data)
}

// ─── Health ───────────────────────────────────────────────────────────────────
export const fetchHealth = () => api.get('/health').then(r => r.data)

export const getFigureUrl = (name: string) => `/api/figures/${name}`

export default api

