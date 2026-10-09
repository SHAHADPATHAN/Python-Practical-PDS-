import React, { useEffect, useState } from 'react'
import { fetchDatasetSummary } from '../services/api'
import { SectionTitle, MetricCard, LoadingState } from '../components/ui'

const DATASET_INVENTORY = [
  { name: 'cj.log (Raw)', stage: 'Raw Input', path: 'Data/raw/cj.log', size: '215 MB', records: '2,061,431', description: 'Semi-structured access log with JSON array elements and unquoted tokens' },
  { name: 'structured_logs.csv', stage: 'Practical 02', path: 'Data/processed/structured_logs.csv', size: '157 MB', records: '2,060,520', description: 'Normalized tabular dataset with parsed JSON structures' },
  { name: 'cleaned_logs.csv', stage: 'Practical 03', path: 'Data/processed/cleaned_logs.csv', size: '235 MB', records: '2,060,520', description: 'Cleaned timestamps, validated IPs/ports, text normalized' },
  { name: 'labeled_logs.csv', stage: 'Practical 04', path: 'Data/processed/labeled_logs.csv', size: '307 MB', records: '2,060,520', description: 'Ground truth attack labels (scanner, suspicious, bot, benign)' },
  { name: 'features.csv', stage: 'Practical 05', path: 'Data/processed/features.csv', size: '746 MB', records: '2,060,520', description: 'Engineered 33+ behavioral, temporal, and lexical features' },
  { name: 'balanced_logs.csv', stage: 'Practical 06', path: 'Data/processed/balanced_logs.csv', size: '6.97 MB', records: '18,304', description: 'Stratified undersampled dataset with 4,576 samples per class' },
  { name: 'ip_summary.csv', stage: 'Practical 07', path: 'Data/processed/ip_summary.csv', size: '243 KB', records: '1,420 IPs', description: 'Aggregated client profiles: ports, paths, volumes, risk scores' },
  { name: 'hourly_activity.csv', stage: 'Practical 07', path: 'Data/processed/hourly_activity.csv', size: '220 KB', records: '24 Hours', description: 'Temporal resampling of volume trends across day' },
  { name: 'label_hour_pivot.csv', stage: 'Practical 07', path: 'Data/processed/label_hour_pivot.csv', size: '140 KB', records: '24 × 4', description: 'Pivot matrix of attack categories across 24 UTC hours' },
  { name: 'filtered_activity.csv', stage: 'Practical 07', path: 'Data/processed/filtered_activity.csv', size: '1.9 MB', records: 'Sub-cohort', description: 'Slices containing exclusively internal subnets and automated bots' },
  { name: 'pipeline_features.csv', stage: 'Practical 10', path: 'Data/processed/pipeline_features.csv', size: '~6.8 MB', records: 'Pipeline Out', description: 'End-to-end automated reusable pipeline transformation output' },
]

const SCHEMA_FIELDS = [
  { field: 'timestamp', type: 'datetime64[ns]', desc: 'Parsed request datetime in UTC format' },
  { field: 'ip', type: 'string (IPv4)', desc: 'Client IPv4 address originating the request' },
  { field: 'port', type: 'int32', desc: 'Destination port (e.g. 80, 443, 8080)' },
  { field: 'method', type: 'category', desc: 'HTTP request method (GET, POST, HEAD, PUT, OPTIONS)' },
  { field: 'path', type: 'string', desc: 'Normalized URI path requested on server' },
  { field: 'response_code', type: 'int16', desc: 'HTTP response status (200, 301, 404, 500)' },
  { field: 'packet_size', type: 'int64', desc: 'Payload byte size returned to client' },
  { field: 'user_agent', type: 'string', desc: 'Client browser or scanning tool user-agent string' },
  { field: 'label', type: 'category', desc: 'Security ground truth: scanner, suspicious, bot, benign' },
]

export default function DatasetPage() {
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDatasetSummary()
      .then((res) => {
        setSummary(res)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  if (loading) return <LoadingState text="Loading dataset inventory..." />

  return (
    <div>
      <SectionTitle
        title="Dataset Architecture & Data Pipeline Inventory"
        sub="Complete provenance and file inventory of raw inputs, intermediate states, and processed feature stores"
      />

      <div className="metric-grid">
        <MetricCard label="Raw Access Log" value="215 MB" sub="2,061,431 raw events" accent="orange" />
        <MetricCard label="Valid Cleaned Rows" value={(summary?.valid_records || 2_060_520).toLocaleString()} sub="99.96% validity" accent="green" />
        <MetricCard label="Total Processed Size" value="> 1.6 GB" sub="Across 10 generated artifacts" accent="purple" />
        <MetricCard label="Balanced Training Matrix" value="18,304 rows" sub="4,576 samples per class" accent="yellow" />
      </div>

      {/* Dataset Artifacts Table */}
      <div className="chart-container" style={{ marginBottom: 24, padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div className="chart-title" style={{ margin: 0 }}>Project Data Files & Provenance</div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Artifact Name</th>
                <th>Pipeline Stage</th>
                <th>File Path</th>
                <th>File Size</th>
                <th>Record Count</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {DATASET_INVENTORY.map((d) => (
                <tr key={d.name}>
                  <td className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                    {d.name}
                  </td>
                  <td>
                    <span className="badge" style={{ background: '#27272a' }}>
                      {d.stage}
                    </span>
                  </td>
                  <td className="mono" style={{ fontSize: '.75rem', color: '#a1a1aa' }}>
                    {d.path}
                  </td>
                  <td className="mono">{d.size}</td>
                  <td className="mono">{d.records}</td>
                  <td style={{ fontSize: '.75rem' }}>{d.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Core Log Schema */}
      <div className="chart-container">
        <div className="chart-title">Canonical Log Schema (Cleaned & Labeled Layer)</div>
        <div style={{ overflowX: 'auto', marginTop: 12 }}>
          <table className="data-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Data Type</th>
                <th>Field Description</th>
              </tr>
            </thead>
            <tbody>
              {SCHEMA_FIELDS.map((s) => (
                <tr key={s.field}>
                  <td className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                    {s.field}
                  </td>
                  <td className="mono" style={{ color: '#a1a1aa', fontSize: '.75rem' }}>
                    {s.type}
                  </td>
                  <td style={{ fontSize: '.8rem' }}>{s.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
