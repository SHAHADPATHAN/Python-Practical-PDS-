import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, ResponsiveContainer, Legend,
} from 'recharts'
import {
  fetchDatasetSummary, fetchLabelDist, fetchTopIps,
  fetchRequestsByHour, fetchScannerBreakdown,
} from '../services/api'
import { MetricCard, LoadingState, SectionTitle } from '../components/ui'

const LABEL_COLORS: Record<string, string> = {
  scanner: '#FF5722',
  suspicious: '#F59E0B',
  bot: '#8B5CF6',
  benign: '#10B981',
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'rgba(13, 19, 34, 0.94)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      boxShadow: '0 12px 30px rgba(0,0,0,0.6), 0 0 15px rgba(255, 107, 0, 0.15)',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: '.75rem',
      minWidth: 140,
    }}>
      <p style={{ color: '#94A3B8', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em' }}>
        {label}
      </p>
      {payload.map((p: any) => (
        <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
          <span style={{ color: p.color || 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color || '#fff' }} />
            {p.name}:
          </span>
          <span style={{ color: '#F8FAFC', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
            {(p.value || 0).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function DashboardPage() {
  const nav = useNavigate()
  const [summary, setSummary]   = useState<any>(null)
  const [labels, setLabels]     = useState<any>(null)
  const [topIps, setTopIps]     = useState<any[]>([])
  const [hourly, setHourly]     = useState<any[]>([])
  const [scanners, setScanners] = useState<any>(null)
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([
      fetchDatasetSummary(),
      fetchLabelDist(),
      fetchTopIps(),
      fetchRequestsByHour(),
      fetchScannerBreakdown(),
    ]).then(([s, l, ips, h, sc]) => {
      setSummary(s); setLabels(l); setTopIps(ips); setHourly(h); setScanners(sc)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState text="Loading executive security dashboard..." />

  const labelData  = labels?.labels || []
  const scannerTools = scanners?.tools?.slice(0, 6) || []

  return (
    <div>
      <SectionTitle
        title="Security Intelligence Operations Center"
        sub="Telemetry & Threat Classification derived from 2,060,520 validated network access records"
      />

      {/* Key metrics */}
      <div className="metric-grid">
        <MetricCard
          label="Total Raw Events"
          value={summary?.total_lines || 2_061_431}
          sub="Raw non-empty logs"
          accent="orange"
        />
        <MetricCard
          label="Valid Parsed"
          value={summary?.valid_records || 2_060_520}
          sub="99.96% schema integrity"
          accent="green"
        />
        <MetricCard
          label="Malformed Events"
          value={summary?.invalid_json || 911}
          sub="Syntax / array errors"
          accent="red"
        />
        <MetricCard
          label="ML Model Accuracy"
          value="99.21%"
          sub="Random Forest (200 trees)"
          accent="purple"
        />
        <MetricCard
          label="Scanner Attacks"
          value={(summary?.label_distribution?.scanner || 1_827_367).toLocaleString()}
          sub="88.68% dominant vector"
          accent="orange"
        />
        <MetricCard
          label="Suspicious Probes"
          value={(summary?.label_distribution?.suspicious || 167_486).toLocaleString()}
          sub="8.13% anomaly events"
          accent="yellow"
        />
        <MetricCard
          label="Automated Bots"
          value={(summary?.label_distribution?.bot || 4_576).toLocaleString()}
          sub="0.22% crawlers & scrapers"
          accent="purple"
        />
        <MetricCard
          label="Benign Traffic"
          value={(summary?.label_distribution?.benign || 61_091).toLocaleString()}
          sub="2.96% legitimate visitors"
          accent="green"
        />
      </div>

      {/* Charts row 1 */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Label distribution donut */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Threat Category Distribution</span>
            <span style={{ fontSize: '.68rem', color: 'var(--text-muted)' }}>2,060,520 TOTAL</span>
          </div>
          <div style={{ position: 'relative' }}>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={labelData}
                  cx="50%" cy="50%"
                  innerRadius={72} outerRadius={110}
                  paddingAngle={4}
                  dataKey="count"
                  nameKey="label"
                  stroke="#0D1322"
                  strokeWidth={3}
                >
                  {labelData.map((entry: any) => (
                    <Cell key={entry.label} fill={LABEL_COLORS[entry.label] || '#64748B'} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  iconType="circle"
                  iconSize={8}
                  formatter={(value) => (
                    <span style={{ fontSize: '.76rem', color: '#CBD5E1', fontWeight: 600, textTransform: 'capitalize' }}>
                      {value}
                    </span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {/* Percentage badge ribbon */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginTop: 12 }}>
            {labelData.map((d: any) => (
              <div key={d.label} style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: '6px 8px',
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '.65rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{d.label}</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '.8rem', color: LABEL_COLORS[d.label] }}>
                  {d.percentage}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Requests by hour */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Diurnal Activity Timeline (24-Hour UTC)</span>
            <span style={{ fontSize: '.68rem', color: 'var(--cyan)' }}>PEAK: 14:00 UTC</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={hourly} margin={{ top: 10, right: 10, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="hourBarGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF6B00" stopOpacity={1} />
                  <stop offset="100%" stopColor="#FF8A34" stopOpacity={0.4} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="hour" tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="requests" name="Hourly Requests" fill="url(#hourBarGrad)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.72rem', color: 'var(--text-muted)', marginTop: 12 }}>
            <span>Off-peak night lull (00h - 04h)</span>
            <span>Intense scanning bursts (08h - 18h)</span>
          </div>
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Top IPs Table */}
        <div className="chart-container" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="chart-title" style={{ margin: 0 }}>Top Threat Actor IPs by Volume</div>
            <button className="btn btn-ghost" style={{ fontSize: '.72rem', padding: '4px 8px' }} onClick={() => nav('/ip-intelligence')}>
              All IPs →
            </button>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>IP Address</th>
                  <th>Request Volume</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {topIps.map((row: any, i: number) => (
                  <tr key={row.ip} onClick={() => nav(`/ip-intelligence?ip=${row.ip}`)} style={{ cursor: 'pointer' }}>
                    <td style={{ color: 'var(--text-muted)' }}>#{i + 1}</td>
                    <td className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>{row.ip}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#F8FAFC' }}>
                      {(row.requests || row.count || 0).toLocaleString()}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '3px 8px', fontSize: '.68rem' }}
                        onClick={(e) => {
                          e.stopPropagation()
                          nav(`/ip-intelligence?ip=${row.ip}`)
                        }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Scanner Tool Breakdown Chart */}
        <div className="chart-container">
          <div className="chart-title">
            <span>Automated Scanner Signatures</span>
            <span style={{ fontSize: '.68rem', color: 'var(--accent)' }}>GOBUSTER DOMINANT</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart
              data={scannerTools}
              layout="vertical"
              margin={{ top: 5, right: 20, bottom: 5, left: 70 }}
            >
              <defs>
                <linearGradient id="scannerBarGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#FF5722" />
                  <stop offset="100%" stopColor="#FFA04D" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }}
                     tickFormatter={v => `${(v/1000).toFixed(0)}k`} tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis type="category" dataKey="tool"
                     tick={{ fill: '#CBD5E1', fontSize: 11, fontFamily: 'var(--font-mono)' }} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="records" name="Detected Records" fill="url(#scannerBarGrad)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Access Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
        {[
          { label: 'Security Intel',  to: '/security',        icon: '⚡', desc: 'Attacks & Fuzzers' },
          { label: 'IP Intelligence', to: '/ip-intelligence', icon: '◎', desc: 'Host Risk Scores' },
          { label: 'EDA Analytics',   to: '/eda',             icon: '∿', desc: 'Heatmaps & Charts' },
          { label: 'Feature Matrix',  to: '/features',        icon: '⊕', desc: '33 Signals' },
          { label: 'ML Playground',   to: '/prediction',      icon: '▶', desc: 'Live Inference' },
          { label: 'Practicals 1-10', to: '/practicals',      icon: '◉', desc: 'Full Reports' },
        ].map(item => (
          <button
            key={item.to}
            className="btn btn-secondary"
            style={{
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              height: 'auto',
              borderRadius: 8,
              textAlign: 'left',
            }}
            onClick={() => nav(item.to)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent)', fontWeight: 700 }}>
              <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
              <span style={{ color: 'var(--text-primary)', fontSize: '.82rem' }}>{item.label}</span>
            </div>
            <div style={{ fontSize: '.7rem', color: 'var(--text-muted)', marginTop: 4 }}>
              {item.desc}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
