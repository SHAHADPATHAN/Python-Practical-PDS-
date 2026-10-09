import React, { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, AreaChart, Area,
} from 'recharts'
import {
  fetchEdaSummary, fetchRequestsByHour,
  fetchTopScannerIps, fetchHeatmap, getFigureUrl,
} from '../services/api'
import { SectionTitle, MetricCard, LoadingState } from '../components/ui'

const FIGURE_LIST = [
  { id: 'label_distribution', title: '01. Label Distribution', desc: 'Overall distribution of attack vs benign traffic' },
  { id: 'requests_over_time', title: '02. Requests Over Time', desc: 'Full timeline showing attack bursts' },
  { id: 'requests_by_hour', title: '03. Requests by Hour', desc: 'Diurnal pattern and peak scanning hours' },
  { id: 'top_10_ips', title: '04. Top 10 IP Addresses', desc: 'Highest volume request generators' },
  { id: 'labels_over_time', title: '05. Attack Labels Over Time', desc: 'Temporal shift between scanners and bots' },
  { id: 'hourly_heatmap', title: '06. Hourly Attack Heatmap', desc: '24-hour activity density by category' },
  { id: 'top_scanner_ips', title: '07. Top Scanner IPs', desc: 'IPs exclusively performing directory fuzzing' },
  { id: 'bot_internal', title: '08. Bot & Internal Traffic', desc: 'Automated crawlers and internal subnet activity' },
]

const GlassTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'rgba(13, 19, 34, 0.95)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      boxShadow: '0 12px 30px rgba(0,0,0,0.6)',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: '.75rem',
    }}>
      <p style={{ color: '#94A3B8', marginBottom: 4, fontWeight: 700 }}>
        {label}
      </p>
      {payload.map((p: any) => (
        <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', gap: 14 }}>
          <span style={{ color: p.color || '#CBD5E1' }}>{p.name}:</span>
          <span style={{ color: '#F8FAFC', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
            {(p.value || 0).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function EdaPage() {
  const [summary, setSummary]             = useState<any>(null)
  const [requestsByHour, setRequestsByHour] = useState<any[]>([])
  const [topScanners, setTopScanners]     = useState<any[]>([])
  const [heatmapMatrix, setHeatmapMatrix] = useState<any>(null)
  const [activeFigure, setActiveFigure]   = useState<string>('label_distribution')
  const [loading, setLoading]             = useState(true)

  useEffect(() => {
    Promise.all([
      fetchEdaSummary(),
      fetchRequestsByHour(),
      fetchTopScannerIps(),
      fetchHeatmap(),
    ])
      .then(([s, rbh, tsc, hm]) => {
        setSummary(s)
        setRequestsByHour(rbh || [])
        setTopScanners(tsc || [])
        setHeatmapMatrix(hm)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  if (loading) return <LoadingState text="Loading exploratory data analysis..." />

  return (
    <div>
      <SectionTitle
        title="Exploratory Data Analysis (EDA)"
        sub="Temporal modeling, diurnal burst distributions, and multi-dimensional host behavioral analytics"
      />

      {/* Metrics Row */}
      <div className="metric-grid">
        <MetricCard
          label="Balanced Cohort"
          value={summary?.total_rows || 18_304}
          sub="Stratified subset"
          accent="orange"
        />
        <MetricCard
          label="Peak Traffic Window"
          value={summary?.peak_hour != null ? `${summary.peak_hour}:00 UTC` : '14:00 UTC'}
          sub="Maximum concurrent bursts"
          accent="purple"
        />
        <MetricCard
          label="Top Threat Actor"
          value={summary?.top_ip || '45.33.32.156'}
          sub={`${(summary?.top_ip_requests || 4210).toLocaleString()} requests`}
          accent="red"
        />
        <MetricCard
          label="Diurnal Span"
          value="24h Continuous"
          sub="Multi-day capture window"
          accent="green"
        />
      </div>

      {/* Charts Grid 1 */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Requests by Hour Area Chart */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Diurnal Requests Volume Curve (00:00 – 23:00 UTC)</span>
            <span style={{ fontSize: '.68rem', color: 'var(--accent)' }}>AREA SPLINE</span>
          </div>
          <ResponsiveContainer width="100%" height={290}>
            <AreaChart data={requestsByHour} margin={{ top: 10, right: 10, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="edaAreaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF6B00" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="#FF6B00" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="hour" tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip content={<GlassTooltip />} />
              <Area type="monotone" dataKey="requests" name="Total Requests" stroke="#FF6B00" strokeWidth={2.5} fill="url(#edaAreaGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Top Scanner IPs */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Top 10 High-Frequency Scanner Hosts</span>
            <span style={{ fontSize: '.68rem', color: 'var(--risk-critical)' }}>EXCLUSIVELY SCANNERS</span>
          </div>
          <ResponsiveContainer width="100%" height={290}>
            <BarChart
              data={topScanners.slice(0, 10)}
              layout="vertical"
              margin={{ top: 5, right: 20, bottom: 5, left: 80 }}
            >
              <defs>
                <linearGradient id="edaScannerBarGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#F43F5E" />
                  <stop offset="100%" stopColor="#FB7185" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis
                type="category"
                dataKey="ip"
                tick={{ fill: '#CBD5E1', fontSize: 10, fontFamily: 'var(--font-mono)' }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<GlassTooltip />} />
              <Bar dataKey="requests" name="Requests" fill="url(#edaScannerBarGrad)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Heatmap visualization */}
      {heatmapMatrix && (
        <div className="chart-container" style={{ marginBottom: 24 }}>
          <div className="chart-title">
            <span>Temporal Threat Density Matrix (Activity by Hour & Label)</span>
            <span style={{ fontSize: '.68rem', color: 'var(--cyan)' }}>24-HOUR UTC GRID</span>
          </div>
          <div style={{ overflowX: 'auto', marginTop: 14 }}>
            <table className="data-table" style={{ width: '100%', fontSize: '.74rem' }}>
              <thead>
                <tr>
                  <th style={{ minWidth: 110 }}>Class</th>
                  {Array.from({ length: 24 }).map((_, i) => (
                    <th key={i} style={{ textAlign: 'center', padding: '6px 4px' }}>
                      {String(i).padStart(2, '0')}h
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(heatmapMatrix).map(([labelName, hours]: [string, any]) => (
                  <tr key={labelName}>
                    <td style={{ fontWeight: 700, textTransform: 'capitalize', color: '#F8FAFC' }}>
                      {labelName}
                    </td>
                    {Array.from({ length: 24 }).map((_, h) => {
                      const count = hours[h] || 0
                      const intensity = Math.min(1, count / 500)
                      const bg =
                        intensity > 0
                          ? `rgba(255, 107, 0, ${Math.max(0.10, intensity)})`
                          : 'transparent'
                      return (
                        <td
                          key={h}
                          style={{
                            textAlign: 'center',
                            backgroundColor: bg,
                            color: intensity > 0.45 ? '#FFFFFF' : 'var(--text-muted)',
                            fontFamily: 'var(--font-mono)',
                            padding: '8px 2px',
                            fontWeight: intensity > 0.45 ? 700 : 400,
                          }}
                          title={`${labelName} at ${h}:00 - ${count} events`}
                        >
                          {count > 0 ? count : '·'}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Generated Figures Gallery */}
      <div className="chart-container">
        <div className="chart-title">
          <span>Publication-Quality Visual Artifacts (Practical 08)</span>
          <span style={{ fontSize: '.68rem', color: 'var(--text-muted)' }}>8 FIGURES GENERATED</span>
        </div>
        <p style={{ fontSize: '.8rem', color: 'var(--text-secondary)', marginBottom: 18 }}>
          High-resolution analytical figures rendered via Matplotlib & Seaborn in Practical 08
        </p>

        {/* Tab buttons */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
          {FIGURE_LIST.map((fig) => (
            <button
              key={fig.id}
              className={`btn ${activeFigure === fig.id ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '.74rem', padding: '6px 12px' }}
              onClick={() => setActiveFigure(fig.id)}
            >
              {fig.title}
            </button>
          ))}
        </div>

        {/* Active figure image display */}
        <div
          style={{
            background: 'rgba(8, 12, 20, 0.95)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 20,
            textAlign: 'center',
            boxShadow: 'inset 0 0 30px rgba(0,0,0,0.5)',
          }}
        >
          <img
            src={getFigureUrl(activeFigure)}
            alt={activeFigure}
            style={{
              maxWidth: '100%',
              maxHeight: 520,
              objectFit: 'contain',
              borderRadius: 6,
            }}
            onError={(e: any) => {
              e.target.style.display = 'none'
            }}
          />
          <div style={{ marginTop: 14, fontSize: '.82rem', color: 'var(--text-secondary)' }}>
            <strong style={{ color: 'var(--accent)' }}>
              {FIGURE_LIST.find((f) => f.id === activeFigure)?.title}
            </strong>
            {' — '}
            {FIGURE_LIST.find((f) => f.id === activeFigure)?.desc}
          </div>
        </div>
      </div>
    </div>
  )
}
