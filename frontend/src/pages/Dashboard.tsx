import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts'
import {
  fetchDatasetSummary, fetchLabelDist, fetchTopIps,
  fetchRequestsByHour, fetchScannerBreakdown,
} from '../services/api'
import { MetricCard, LoadingState, SectionTitle } from '../components/ui'

const THREAT_META: Record<string, {
  label: string
  sublabel: string
  risk: string
  riskColor: string
  desc: string
  gradient: [string, string]
  color: string
}> = {
  scanner: {
    label: 'Scanner Attacks',
    sublabel: 'Reconnaissance',
    risk: 'CRITICAL',
    riskColor: '#FF4500',
    desc: 'Gobuster, Nikto & automated directory fuzzers',
    gradient: ['#FF3838', '#FF7A00'],
    color: '#FF6B00',
  },
  suspicious: {
    label: 'Suspicious Probes',
    sublabel: 'Anomalies',
    risk: 'ELEVATED',
    riskColor: '#F59E0B',
    desc: 'Anomaly 4xx bursts, SQLi syntax & path traversal',
    gradient: ['#F59E0B', '#FCD34D'],
    color: '#F59E0B',
  },
  benign: {
    label: 'Benign Traffic',
    sublabel: 'Clean Access',
    risk: 'VERIFIED',
    riskColor: '#10B981',
    desc: 'Legitimate human visitors & regular asset loads',
    gradient: ['#059669', '#10B981'],
    color: '#10B981',
  },
  bot: {
    label: 'Automated Bots',
    sublabel: 'Spiders',
    risk: 'CRAWLER',
    riskColor: '#8B5CF6',
    desc: 'Search spiders, cURL probes & headless scripts',
    gradient: ['#7C3AED', '#C084FC'],
    color: '#8B5CF6',
  },
}

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

  const [activeDonutIndex, setActiveDonutIndex] = useState<number | null>(null)

  const activeItem = activeDonutIndex !== null ? labelData[activeDonutIndex] : null
  const activeMeta = activeItem ? (THREAT_META[activeItem.label?.toLowerCase()] || {
    label: activeItem.label,
    sublabel: 'Traffic',
    risk: 'ACTIVE',
    riskColor: '#FF6B00',
    desc: '',
    gradient: ['#FF6B00', '#FF8A34'] as [string, string],
    color: '#FF6B00',
  }) : null

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
      <div className="grid-2" style={{ marginBottom: 24, alignItems: 'stretch' }}>
        {/* Label distribution donut */}
        <div className="chart-container" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div className="chart-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: '#FF6B00',
                  boxShadow: '0 0 10px #FF6B00',
                  display: 'inline-block',
                }} />
                <span>Threat Category Distribution</span>
              </div>
              <span style={{
                fontSize: '.62rem',
                fontFamily: 'var(--font-mono)',
                background: 'rgba(255, 107, 0, 0.12)',
                border: '1px solid rgba(255, 107, 0, 0.3)',
                color: '#FF8A34',
                padding: '2px 8px',
                borderRadius: 4,
                fontWeight: 700,
                letterSpacing: '.05em',
              }}>
                DOMINANT: SCANNER (88.7%)
              </span>
            </div>

            {/* Donut chart with Center HUD */}
            <div style={{ position: 'relative', height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {/* Radar guide circles */}
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: 236,
                height: 236,
                borderRadius: '50%',
                border: '1px dashed rgba(255, 255, 255, 0.06)',
                pointerEvents: 'none',
              }} />
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: 142,
                height: 142,
                borderRadius: '50%',
                border: '1px solid rgba(255, 255, 255, 0.04)',
                pointerEvents: 'none',
              }} />

              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <defs>
                    <linearGradient id="donutGrad-scanner" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#FF3838" />
                      <stop offset="100%" stopColor="#FF7A00" />
                    </linearGradient>
                    <linearGradient id="donutGrad-suspicious" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#F59E0B" />
                      <stop offset="100%" stopColor="#FCD34D" />
                    </linearGradient>
                    <linearGradient id="donutGrad-benign" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#059669" />
                      <stop offset="100%" stopColor="#10B981" />
                    </linearGradient>
                    <linearGradient id="donutGrad-bot" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#7C3AED" />
                      <stop offset="100%" stopColor="#C084FC" />
                    </linearGradient>
                  </defs>
                  <Pie
                    data={labelData}
                    cx="50%" cy="50%"
                    innerRadius={72} outerRadius={108}
                    paddingAngle={4}
                    cornerRadius={6}
                    dataKey="count"
                    nameKey="label"
                    stroke="#080C14"
                    strokeWidth={2}
                  >
                    {labelData.map((entry: any, index: number) => {
                      const isSelected = activeDonutIndex === index
                      return (
                        <Cell
                          key={entry.label}
                          fill={`url(#donutGrad-${entry.label?.toLowerCase()})`}
                          stroke={isSelected ? '#FFFFFF' : '#080C14'}
                          strokeWidth={isSelected ? 3 : 2}
                          style={{
                            filter: isSelected ? 'drop-shadow(0 0 12px rgba(255, 107, 0, 0.75))' : 'none',
                            cursor: 'pointer',
                            transition: 'all 0.25s ease',
                          }}
                          onMouseEnter={() => setActiveDonutIndex(index)}
                          onMouseLeave={() => setActiveDonutIndex(null)}
                        />
                      )
                    })}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>

              {/* Center Telemetry HUD */}
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: 126,
                height: 126,
                borderRadius: '50%',
                background: 'radial-gradient(circle, #0F172A 0%, #080C14 100%)',
                border: activeMeta ? `1px solid ${activeMeta.color}66` : '1px solid rgba(255, 255, 255, 0.08)',
                boxShadow: activeMeta
                  ? `0 0 25px rgba(0,0,0,0.85), 0 0 16px ${activeMeta.color}33, inset 0 0 12px ${activeMeta.color}22`
                  : '0 0 25px rgba(0,0,0,0.85), inset 0 0 15px rgba(255, 107, 0, 0.05)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                pointerEvents: 'none',
                padding: 10,
                transition: 'all 0.25s ease',
                zIndex: 10,
              }}>
                {activeItem && activeMeta ? (
                  <>
                    <div style={{
                      fontSize: '.56rem',
                      fontWeight: 700,
                      letterSpacing: '.08em',
                      color: activeMeta.color,
                      textTransform: 'uppercase',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                    }}>
                      <span style={{
                        width: 5,
                        height: 5,
                        borderRadius: '50%',
                        background: activeMeta.color,
                        boxShadow: `0 0 6px ${activeMeta.color}`,
                      }} />
                      {activeItem.label}
                    </div>
                    <div style={{
                      fontSize: '1.65rem',
                      fontWeight: 800,
                      fontFamily: 'var(--font-mono)',
                      color: '#F8FAFC',
                      lineHeight: 1.05,
                      margin: '2px 0',
                    }}>
                      {activeItem.percentage}%
                    </div>
                    <div style={{
                      fontSize: '.62rem',
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--text-secondary)',
                    }}>
                      {Number(activeItem.count).toLocaleString()} recs
                    </div>
                  </>
                ) : (
                  <>
                    <span style={{
                      fontSize: '.55rem',
                      color: '#94A3B8',
                      fontWeight: 700,
                      letterSpacing: '.12em',
                      textTransform: 'uppercase',
                    }}>
                      TOTAL EVENTS
                    </span>
                    <span style={{
                      fontSize: '1.65rem',
                      fontWeight: 800,
                      fontFamily: 'var(--font-mono)',
                      color: '#F8FAFC',
                      lineHeight: 1.05,
                      margin: '2px 0',
                      background: 'linear-gradient(180deg, #FFFFFF 20%, #CBD5E1 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}>
                      2.06M
                    </span>
                    <span style={{
                      fontSize: '.55rem',
                      color: 'var(--cyan)',
                      background: 'rgba(6, 182, 212, 0.1)',
                      border: '1px solid rgba(6, 182, 212, 0.25)',
                      padding: '1px 6px',
                      borderRadius: 4,
                      fontWeight: 700,
                      letterSpacing: '.05em',
                    }}>
                      99.96% VALID
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* High-density interactive threat category matrix */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: 10,
            marginTop: 14,
          }}>
            {labelData.map((d: any, i: number) => {
              const meta = THREAT_META[d.label?.toLowerCase()] || {
                label: d.label,
                sublabel: '',
                risk: 'UNKNOWN',
                riskColor: '#64748B',
                desc: '',
                gradient: ['#64748B', '#94A3B8'] as [string, string],
                color: '#64748B',
              }
              const isActive = activeDonutIndex === i

              return (
                <div
                  key={d.label}
                  onMouseEnter={() => setActiveDonutIndex(i)}
                  onMouseLeave={() => setActiveDonutIndex(null)}
                  style={{
                    background: isActive ? 'rgba(255, 255, 255, 0.05)' : 'rgba(15, 23, 40, 0.65)',
                    border: `1px solid ${isActive ? meta.color : 'rgba(255, 255, 255, 0.08)'}`,
                    boxShadow: isActive ? `0 4px 16px ${meta.color}25` : 'none',
                    borderRadius: 8,
                    padding: '10px 12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  {/* Left accent strip */}
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    bottom: 0,
                    width: 3,
                    background: `linear-gradient(180deg, ${meta.gradient[0]}, ${meta.gradient[1]})`,
                  }} />

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{
                        width: 7,
                        height: 7,
                        borderRadius: '50%',
                        background: meta.color,
                        boxShadow: isActive ? `0 0 8px ${meta.color}` : 'none',
                      }} />
                      <span style={{
                        fontSize: '.74rem',
                        fontWeight: 700,
                        color: isActive ? '#F8FAFC' : '#CBD5E1',
                        textTransform: 'capitalize',
                      }}>
                        {meta.label}
                      </span>
                    </div>
                    <span style={{
                      fontSize: '.56rem',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 700,
                      color: meta.riskColor,
                      background: `${meta.riskColor}18`,
                      border: `1px solid ${meta.riskColor}40`,
                      padding: '1px 6px',
                      borderRadius: 3,
                      letterSpacing: '.06em',
                    }}>
                      {meta.risk}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginTop: 2 }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 800,
                      fontSize: '.95rem',
                      color: meta.color,
                    }}>
                      {d.percentage}%
                    </span>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '.7rem',
                      color: 'var(--text-muted)',
                    }}>
                      {Number(d.count).toLocaleString()} recs
                    </span>
                  </div>

                  {/* Visual ratio bar */}
                  <div style={{
                    height: 3,
                    background: 'rgba(255, 255, 255, 0.06)',
                    borderRadius: 2,
                    overflow: 'hidden',
                    marginTop: 6,
                  }}>
                    <div style={{
                      height: '100%',
                      width: `${Math.max(d.percentage, 0.8)}%`,
                      background: `linear-gradient(90deg, ${meta.gradient[0]}, ${meta.gradient[1]})`,
                      borderRadius: 2,
                      transition: 'width 0.4s ease',
                    }} />
                  </div>

                  <div style={{
                    fontSize: '.62rem',
                    color: 'var(--text-muted)',
                    marginTop: 5,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}>
                    {meta.desc}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Requests by hour */}
        <div className="chart-container" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div className="chart-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: 'var(--cyan)',
                  boxShadow: '0 0 10px var(--cyan)',
                  display: 'inline-block',
                }} />
                <span>Diurnal Activity Timeline (24-Hour UTC)</span>
              </div>
              <span style={{
                fontSize: '.62rem',
                fontFamily: 'var(--font-mono)',
                background: 'rgba(6, 182, 212, 0.12)',
                border: '1px solid rgba(6, 182, 212, 0.3)',
                color: 'var(--cyan)',
                padding: '2px 8px',
                borderRadius: 4,
                fontWeight: 700,
                letterSpacing: '.05em',
              }}>
                PEAK: 08:00 & 14:00-15:00 UTC
              </span>
            </div>

            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={hourly} margin={{ top: 10, right: 10, bottom: 5, left: 0 }}>
                <defs>
                  <linearGradient id="hourBarGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#06B6D4" stopOpacity={1} />
                    <stop offset="60%" stopColor="#3B82F6" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="#1E3A8A" stopOpacity={0.3} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="hour" tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="requests" name="Hourly Requests" fill="url(#hourBarGrad)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Diurnal telemetry stats matrix */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 10,
            marginTop: 14,
          }}>
            <div style={{
              background: 'rgba(15, 23, 40, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: 8,
              padding: '10px 12px',
            }}>
              <div style={{ fontSize: '.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em' }}>
                Primary Burst
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.95rem', fontWeight: 700, color: 'var(--cyan)', marginTop: 2 }}>
                08:00 UTC
              </div>
              <div style={{ fontSize: '.62rem', color: '#CBD5E1', marginTop: 2 }}>
                2,099 reqs / hour
              </div>
            </div>

            <div style={{
              background: 'rgba(15, 23, 40, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: 8,
              padding: '10px 12px',
            }}>
              <div style={{ fontSize: '.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em' }}>
                Secondary Peak
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.95rem', fontWeight: 700, color: '#3B82F6', marginTop: 2 }}>
                14:00-15:00 UTC
              </div>
              <div style={{ fontSize: '.62rem', color: '#CBD5E1', marginTop: 2 }}>
                1,228 reqs / hour
              </div>
            </div>

            <div style={{
              background: 'rgba(15, 23, 40, 0.65)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: 8,
              padding: '10px 12px',
            }}>
              <div style={{ fontSize: '.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em' }}>
                Off-Peak Lull
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.95rem', fontWeight: 700, color: '#94A3B8', marginTop: 2 }}>
                20:00 UTC
              </div>
              <div style={{ fontSize: '.62rem', color: '#CBD5E1', marginTop: 2 }}>
                389 reqs (5.4x dip)
              </div>
            </div>
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
