import React, { useEffect, useState } from 'react'
import { fetchReports, fetchReport } from '../services/api'
import { SectionTitle, LoadingState } from '../components/ui'

export default function ReportsPage() {
  const [reports, setReports]       = useState<any[]>([])
  const [activeKey, setActiveKey]   = useState<string>('classifier')
  const [reportData, setReportData] = useState<any | null>(null)
  const [loading, setLoading]       = useState(true)
  const [reportLoading, setReportLoading] = useState(false)

  useEffect(() => {
    fetchReports()
      .then((res) => {
        setReports(res || [])
        setLoading(false)
        if (res && res.length > 0) {
          const firstKey = res.find((r: any) => r.key === 'classifier')?.key || res[0].key
          setActiveKey(firstKey)
          loadReportContent(firstKey)
        }
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  const loadReportContent = (key: string) => {
    setReportLoading(true)
    fetchReport(key)
      .then((res) => {
        setReportData(res)
        setReportLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setReportLoading(false)
      })
  }

  const handleSelectReport = (key: string) => {
    setActiveKey(key)
    loadReportContent(key)
  }

  if (loading) return <LoadingState text="Loading reports inventory..." />

  return (
    <div>
      <SectionTitle
        title="Analytical Reports Archive"
        sub="Comprehensive output logs, validation checks, and metric summaries generated across practicals"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 24, alignItems: 'flex-start' }}>
        {/* Reports Nav */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {reports.map((r) => {
            const isActive = activeKey === r.key
            return (
              <button
                key={r.key}
                type="button"
                onClick={() => handleSelectReport(r.key)}
                className="btn"
                style={{
                  backgroundColor: isActive ? 'var(--bg-card-hover)' : 'var(--bg-card)',
                  border: `1px solid ${isActive ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 6,
                  padding: '12px 14px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  textAlign: 'left',
                  width: '100%',
                }}
              >
                <div>
                  <div
                    className="mono"
                    style={{
                      fontSize: '.8rem',
                      fontWeight: 600,
                      color: isActive ? 'var(--accent)' : 'var(--text-primary)',
                    }}
                  >
                    {r.filename}
                  </div>
                  <div style={{ fontSize: '.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                    {(r.size_bytes / 1024).toFixed(1)} KB
                  </div>
                </div>
                <span
                  className="badge"
                  style={{
                    backgroundColor: r.available ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: r.available ? '#22c55e' : '#ef4444',
                    fontSize: '.65rem',
                  }}
                >
                  {r.available ? 'AVAILABLE' : 'MISSING'}
                </span>
              </button>
            )
          })}
        </div>

        {/* Report Content */}
        <div className="chart-container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <div className="chart-title" style={{ margin: 0 }}>
                {reportData?.filename || 'Report Viewer'}
              </div>
              <div style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>
                Size: {((reportData?.size_bytes || 0) / 1024).toFixed(2)} KB | Location: outputs/reports/
              </div>
            </div>
            {reportData?.content && (
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '.75rem' }}
                  onClick={() => {
                    navigator.clipboard.writeText(reportData.content)
                    alert('Copied report to clipboard!')
                  }}
                >
                  Copy Text
                </button>
                <button
                  className="btn btn-primary"
                  style={{ fontSize: '.75rem' }}
                  onClick={() => {
                    const blob = new Blob([reportData.content], { type: 'text/plain' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = reportData.filename
                    a.click()
                  }}
                >
                  Download .txt
                </button>
              </div>
            )}
          </div>

          {reportLoading ? (
            <LoadingState text="Loading report text..." />
          ) : reportData?.content ? (
            <pre
              style={{
                backgroundColor: '#0a0a0a',
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: 16,
                fontSize: '.75rem',
                fontFamily: 'var(--font-mono)',
                color: '#e4e4e7',
                maxHeight: 600,
                overflowY: 'auto',
                whiteSpace: 'pre-wrap',
                lineHeight: 1.5,
              }}
            >
              {reportData.content}
            </pre>
          ) : (
            <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
              Report content is not available.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
