import React, { useState } from 'react'
import { uploadLog } from '../services/api'
import { SectionTitle, MetricCard, LabelBadge, LoadingState } from '../components/ui'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [parserHint, setParserHint] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)
  const [dragOver, setDragOver] = useState<boolean>(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select or drop a log file first.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const res = await uploadLog(file, parserHint || undefined)
      setResult(res)
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Upload processing failed.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const loadDemoLog = () => {
    const demoContent = `[18/Jan/2024:06:12:01 +0000] 192.168.1.100 "GET /admin/login.php HTTP/1.1" 200 4520 "Gobuster/v3.1.0"
[18/Jan/2024:06:12:02 +0000] 192.168.1.100 "GET /wp-config.php.bak HTTP/1.1" 404 182 "Gobuster/v3.1.0"
[18/Jan/2024:06:12:03 +0000] 192.168.1.100 "GET /.env HTTP/1.1" 404 182 "Gobuster/v3.1.0"
[18/Jan/2024:06:12:04 +0000] 10.0.0.15 "GET /api/v1/health HTTP/1.1" 200 84 "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
[18/Jan/2024:06:12:05 +0000] 45.33.32.156 "GET /setup.cgi?next_file=netgear.cfg HTTP/1.1" 404 230 "Nmap Scripting Engine"
[18/Jan/2024:06:12:06 +0000] 10.0.0.22 "GET /index.html HTTP/1.1" 200 3512 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
[18/Jan/2024:06:12:07 +0000] 192.168.1.105 "POST /xmlrpc.php HTTP/1.1" 403 145 "python-requests/2.28.1"
`
    const demoBlob = new Blob([demoContent], { type: 'text/plain' })
    const demoFile = new File([demoBlob], 'sample_security_log.log', { type: 'text/plain' })
    setFile(demoFile)
    setError(null)
  }

  return (
    <div>
      <SectionTitle
        title="Log Ingestion & Live Parsing Pipeline"
        sub="Upload external log files (Apache, Nginx, JSON, CJ format) to parse, classify attacks, and extract features in real time"
      />

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Upload Box */}
        <div className="chart-container">
          <div className="chart-title">Upload File</div>
          <div
            onDragOver={(e) => {
              e.preventDefault()
              setDragOver(true)
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragOver ? 'var(--accent)' : 'var(--border-strong)'}`,
              borderRadius: 8,
              padding: 32,
              textAlign: 'center',
              backgroundColor: dragOver ? 'var(--accent-dim)' : 'rgba(255,255,255,.02)',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".log,.txt,.csv,.json,.jsonl"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <div style={{ fontSize: '2.4rem', marginBottom: 8, color: 'var(--accent)' }}>↑</div>
            <div style={{ fontWeight: 600, fontSize: '.95rem', marginBottom: 4 }}>
              {file ? file.name : 'Choose a file or drag & drop here'}
            </div>
            <div style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>
              {file
                ? `${(file.size / 1024).toFixed(1)} KB — Ready to analyze`
                : 'Supports .log, .txt, .csv, .json, .jsonl (up to 500 MB)'}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 16, alignItems: 'center' }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: '.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                Parser Engine
              </label>
              <select
                className="select"
                value={parserHint}
                onChange={(e) => setParserHint(e.target.value)}
                style={{ width: '100%' }}
              >
                <option value="">Auto-Detect Format (Recommended)</option>
                <option value="universal">Universal Web Log / Syslog (Heuristic)</option>
                <option value="apache">Apache Combined / Common</option>
                <option value="nginx">Nginx Standard Access Log</option>
                <option value="cj_log">CJ Log Array (University Project)</option>
                <option value="csv">Structured CSV / TSV</option>
                <option value="json">JSON Lines / JSON Objects</option>
              </select>
            </div>
            <div style={{ alignSelf: 'flex-end' }}>
              <button
                className="btn btn-secondary"
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  loadDemoLog()
                }}
              >
                Load Sample
              </button>
            </div>
          </div>

          {error && (
            <div
              style={{
                marginTop: 14,
                padding: '10px 14px',
                borderRadius: 6,
                background: 'rgba(239,68,68,0.15)',
                border: '1px solid #ef4444',
                color: '#f87171',
                fontSize: '.8rem',
              }}
            >
              {error}
            </div>
          )}

          <div style={{ marginTop: 20 }}>
            <button
              className="btn btn-primary"
              style={{ width: '100%', padding: '10px' }}
              onClick={handleUpload}
              disabled={loading || !file}
            >
              {loading ? 'Processing through Pipeline...' : 'Run Analysis Pipeline'}
            </button>
          </div>
        </div>

        {/* Pipeline Info / Instructions */}
        <div className="chart-container">
          <div className="chart-title">Automated Analysis Steps</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              {
                step: '01',
                title: 'Format Detection & Parsing',
                desc: 'Identifies delimiters, regex structures, JSON tokens, and Apache/Nginx format flags.',
              },
              {
                step: '02',
                title: 'Data Cleaning & Normalization',
                desc: 'Converts HTTP timestamps, standardizes IP strings, extracts HTTP method and status codes.',
              },
              {
                step: '03',
                title: 'Security Attack Labeling',
                desc: 'Scans for Gobuster, DirBuster, Nmap, Nikto signatures, automated bots, and high-frequency scan patterns.',
              },
              {
                step: '04',
                title: 'Feature Extraction & Threat Score',
                desc: 'Computes request rates per minute, port variances, and threat risk scoring per client IP.',
              },
            ].map((s) => (
              <div key={s.step} style={{ display: 'flex', gap: 12 }}>
                <div
                  className="mono"
                  style={{
                    color: 'var(--accent)',
                    fontWeight: 700,
                    fontSize: '1rem',
                    minWidth: 28,
                  }}
                >
                  {s.step}
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '.85rem', color: 'var(--text-primary)' }}>
                    {s.title}
                  </div>
                  <div style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {loading && <LoadingState text="Parsing file, running attack detection heuristics, and extracting features..." />}

      {/* Analysis Results */}
      {result && result.status === 'error' && (
        <div
          className="chart-container"
          style={{
            marginTop: 24,
            borderColor: '#ef4444',
            background: 'rgba(239, 68, 68, 0.08)',
          }}
        >
          <div style={{ color: '#ef4444', fontWeight: 600, fontSize: '1rem', marginBottom: 8 }}>
            Pipeline Parsing Error
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '.85rem' }}>
            {result.message || 'No valid records could be extracted from this log file.'}
          </div>
          <div style={{ marginTop: 12, fontSize: '.8rem', color: 'var(--text-muted)' }}>
            Detected parser: <span className="mono">{result.detected_format}</span> | Lines processed:{' '}
            {result.total_lines}
          </div>
        </div>
      )}

      {result && result.status !== 'error' && (
        <div style={{ marginTop: 24 }}>
          <div className="page-header">
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Pipeline Analysis Results</h2>
              <p style={{ fontSize: '.8rem', color: 'var(--text-muted)' }}>
                Parser engine:{' '}
                <strong className="mono" style={{ color: 'var(--accent)' }}>
                  {result.parser_used || result.parser_name || 'Universal Web Log'}
                </strong>{' '}
                | Total records: <strong>{Number(result.valid_records || 0).toLocaleString()}</strong>
                {result.timestamp_min && (
                  <span>
                    {' '}
                    | Period: <span className="mono">{result.timestamp_min.slice(0, 19)}</span> to{' '}
                    <span className="mono">{result.timestamp_max?.slice(0, 19)}</span>
                  </span>
                )}
              </p>
            </div>
            {(result.records || result.sample_records)?.length > 0 && (
              <button
                className="btn btn-secondary"
                onClick={() => {
                  const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `pipeline_result_${Date.now()}.json`
                  a.click()
                }}
              >
                Download Report JSON
              </button>
            )}
          </div>

          <div className="metric-grid">
            <MetricCard
              label="Total Lines Processed"
              value={result.total_lines || 0}
              sub="Lines in uploaded file"
              accent="default"
            />
            <MetricCard
              label="Valid Records"
              value={result.valid_records || (result.records ? result.records.length : 0)}
              sub="Successfully parsed"
              accent="green"
            />
            <MetricCard
              label="Invalid / Skipped"
              value={result.invalid_lines || result.invalid_records || 0}
              sub="Syntax mismatch or comments"
              accent={result.invalid_lines > 0 ? 'red' : 'default'}
            />
            <MetricCard
              label="Unique Client IPs"
              value={result.unique_ips || 0}
              sub="Distinct sources identified"
              accent="purple"
            />
            <MetricCard
              label="Threat Detections"
              value={
                (result.label_distribution?.scanner || 0) +
                (result.label_distribution?.suspicious || 0) +
                (result.label_distribution?.bot || 0)
              }
              sub="Attacks, bots & scans"
              accent="orange"
            />
            <MetricCard
              label="Avg Threat Score"
              value={`${result.threat_score_avg || 0} / 100`}
              sub="Overall dataset risk"
              accent={(result.threat_score_avg || 0) > 50 ? 'red' : 'default'}
            />
          </div>

          <div className="grid-2" style={{ marginBottom: 20 }}>
            {result.label_distribution && (
              <div className="chart-container">
                <div className="chart-title">Detected Label Breakdown</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {Object.entries(result.label_distribution).map(([k, v]: [string, any]) => {
                    const total = Number(result.valid_records) || 1
                    const pct = ((Number(v) / total) * 100).toFixed(1)
                    return (
                      <div key={k}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, alignItems: 'center' }}>
                          <LabelBadge label={k} />
                          <span className="mono" style={{ fontSize: '.8rem', color: 'var(--text-secondary)' }}>
                            {Number(v).toLocaleString()} ({pct}%)
                          </span>
                        </div>
                        <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
                          <div
                            style={{
                              height: '100%',
                              width: `${pct}%`,
                              background:
                                k === 'scanner'
                                  ? '#ef4444'
                                  : k === 'suspicious'
                                  ? '#f97316'
                                  : k === 'bot'
                                  ? '#06b6d4'
                                  : '#10b981',
                              borderRadius: 3,
                            }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {result.top_ips && result.top_ips.length > 0 && (
              <div className="chart-container">
                <div className="chart-title">Top Client IP Addresses</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {result.top_ips.slice(0, 6).map((item: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '6px 10px',
                        background: 'rgba(255,255,255,0.02)',
                        borderRadius: 6,
                        border: '1px solid var(--border)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: '.75rem', color: 'var(--text-muted)', width: 16 }}>#{idx + 1}</span>
                        <span className="mono" style={{ fontSize: '.85rem', color: 'var(--accent)' }}>
                          {item.ip}
                        </span>
                      </div>
                      <span className="mono badge" style={{ fontSize: '.75rem' }}>
                        {item.count.toLocaleString()} reqs
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {(result.records || result.sample_records) && (result.records || result.sample_records).length > 0 && (
            <div className="chart-container" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div className="chart-title" style={{ margin: 0 }}>
                  Parsed Records Preview (Showing first {(result.records || result.sample_records).slice(0, 50).length})
                </div>
                <div style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>
                  Total {Number(result.valid_records).toLocaleString()} records processed
                </div>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table" style={{ width: '100%' }}>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Timestamp</th>
                      <th>Client IP</th>
                      <th>Method</th>
                      <th>Path / Resource</th>
                      <th>Status</th>
                      <th>Risk Score</th>
                      <th>Classification</th>
                      <th>User Agent / Signatures</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(result.records || result.sample_records).slice(0, 50).map((r: any, idx: number) => {
                      const riskVal = r.risk_score != null ? Number(r.risk_score) : null
                      return (
                        <tr key={idx}>
                          <td style={{ color: 'var(--text-muted)' }}>{idx + 1}</td>
                          <td className="mono" style={{ fontSize: '.75rem', whiteSpace: 'nowrap' }}>
                            {r.timestamp || r.time || '—'}
                          </td>
                          <td className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                            {r.ip || r.client_ip || '—'}
                          </td>
                          <td>
                            <span className="badge">{r.method || 'GET'}</span>
                          </td>
                          <td
                            className="mono"
                            style={{
                              maxWidth: 240,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              fontSize: '.75rem',
                            }}
                            title={r.path || r.url || '/'}
                          >
                            {r.path || r.url || '/'}
                          </td>
                          <td className="mono">
                            <span
                              style={{
                                color:
                                  (r.response_code || r.status) >= 500
                                    ? '#ef4444'
                                    : (r.response_code || r.status) >= 400
                                    ? '#f97316'
                                    : '#10b981',
                              }}
                            >
                              {r.response_code || r.status || 200}
                            </span>
                          </td>
                          <td>
                            {riskVal != null ? (
                              <span
                                className="mono"
                                style={{
                                  fontSize: '.75rem',
                                  padding: '2px 6px',
                                  borderRadius: 4,
                                  background:
                                    riskVal >= 70
                                      ? 'rgba(239,68,68,0.2)'
                                      : riskVal >= 40
                                      ? 'rgba(249,115,22,0.2)'
                                      : 'rgba(16,185,129,0.15)',
                                  color:
                                    riskVal >= 70
                                      ? '#f87171'
                                      : riskVal >= 40
                                      ? '#fb923c'
                                      : '#34d399',
                                }}
                              >
                                {riskVal} / 100
                              </span>
                            ) : (
                              '—'
                            )}
                          </td>
                          <td>
                            <LabelBadge label={r.label || 'benign'} />
                          </td>
                          <td
                            className="mono"
                            style={{
                              maxWidth: 220,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              fontSize: '.75rem',
                              color: 'var(--text-muted)',
                            }}
                            title={r.user_agent || 'unknown'}
                          >
                            {r.user_agent || r.scanner_type || '—'}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
