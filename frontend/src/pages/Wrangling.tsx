import React, { useState, useEffect } from 'react'
import { fetchHourlyActivity, fetchHeatmap, fetchTopIpsFull } from '../services/api'
import { SectionTitle, MetricCard, LoadingState, LabelBadge } from '../components/ui'

export default function WranglingPage() {
  const [activeTab, setActiveTab] = useState<'ip_summary' | 'hourly_pivot' | 'filtered_activity'>('ip_summary')
  const [topIps, setTopIps] = useState<any[]>([])
  const [hourly, setHourly] = useState<any[]>([])
  const [pivot, setPivot] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    Promise.all([
      fetchTopIpsFull(25),
      fetchHourlyActivity(),
      fetchHeatmap(),
    ])
      .then(([ips, h, hm]) => {
        setTopIps(ips || [])
        setHourly(h || [])
        setPivot(hm || null)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  if (loading) return <LoadingState text="Loading data wrangling tables..." />

  return (
    <div>
      <SectionTitle
        title="Data Wrangling & Aggregation"
        sub="Practical 07: Resampling, multidimensional pivot tables, high-risk subset slicing, and IP profiling"
      />

      {/* Metrics */}
      <div className="metric-grid">
        <MetricCard label="IP Profiles Created" value="3,430 IPs" sub="ip_summary.csv (243 KB)" accent="orange" />
        <MetricCard label="Hourly Time-Series" value="9,782 Hours" sub="hourly_activity.csv (220 KB)" accent="purple" />
        <MetricCard label="Multidimensional Pivot" value="4,956 Cells" sub="label_hour_pivot.csv (140 KB)" accent="green" />
        <MetricCard label="Filtered High-Risk" value="5,333 Events" sub="filtered_activity.csv (1.9 MB)" accent="red" />
      </div>

      {/* Tab Selectors */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        <button
          className={`btn ${activeTab === 'ip_summary' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('ip_summary')}
        >
          IP Aggregation Summary (ip_summary.csv)
        </button>
        <button
          className={`btn ${activeTab === 'hourly_pivot' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('hourly_pivot')}
        >
          Hourly Cross-Tab Pivot (label_hour_pivot.csv)
        </button>
        <button
          className={`btn ${activeTab === 'filtered_activity' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('filtered_activity')}
        >
          High-Risk Threat Subset (filtered_activity.csv)
        </button>
      </div>

      {/* Tab 1: IP Summary */}
      {activeTab === 'ip_summary' && (
        <div className="chart-container" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
            <div className="chart-title" style={{ margin: 0 }}>Client IP Aggregation Matrix (Top 25)</div>
            <p style={{ fontSize: '.75rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
              Engineered via Pandas groupby aggregation: request volume, unique target ports, unique URI paths, and threat rates.
            </p>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>#</th>
                  <th>IP Address</th>
                  <th>Requests</th>
                  <th>Unique Ports</th>
                  <th>Unique Paths</th>
                  <th>Risk Tier</th>
                  <th>Dominant Behavior</th>
                </tr>
              </thead>
              <tbody>
                {topIps.map((ip, idx) => (
                  <tr key={ip.ip}>
                    <td style={{ color: 'var(--text-muted)' }}>{idx + 1}</td>
                    <td className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                      {ip.ip}
                    </td>
                    <td className="mono">{(ip.requests || ip.count || 0).toLocaleString()}</td>
                    <td className="mono">{ip.unique_ports || ip.ports || 1}</td>
                    <td className="mono">{ip.unique_paths || ip.paths || 120}</td>
                    <td>
                      <span
                        className="badge"
                        style={{
                          background:
                            ip.risk_score >= 80
                              ? 'rgba(239,68,68,0.2)'
                              : ip.risk_score >= 50
                              ? 'rgba(249,115,22,0.2)'
                              : 'rgba(34,197,94,0.2)',
                          color:
                            ip.risk_score >= 80
                              ? '#ef4444'
                              : ip.risk_score >= 50
                              ? '#f97316'
                              : '#22c55e',
                        }}
                      >
                        {ip.risk_score ? `${ip.risk_score}/100` : ip.risk_level || 'HIGH'}
                      </span>
                    </td>
                    <td>
                      <LabelBadge label={ip.dominant_label || 'scanner'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Hourly Pivot */}
      {activeTab === 'hourly_pivot' && (
        <div className="chart-container" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
            <div className="chart-title" style={{ margin: 0 }}>Label × Hour Pivot Matrix (24-Hour Distribution)</div>
            <p style={{ fontSize: '.75rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
              Computed using <code>pd.pivot_table(index='hour', columns='label', values='request_id', aggfunc='count')</code>.
            </p>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ width: '100%', fontSize: '.8rem' }}>
              <thead>
                <tr>
                  <th>Hour (UTC)</th>
                  <th style={{ color: 'var(--label-scanner)' }}>Scanner</th>
                  <th style={{ color: 'var(--label-suspicious)' }}>Suspicious</th>
                  <th style={{ color: 'var(--label-bot)' }}>Bot</th>
                  <th style={{ color: 'var(--label-benign)' }}>Benign</th>
                  <th>Total Activity</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: 24 }).map((_, h) => {
                  const sc = pivot?.scanner?.[h] || 0
                  const su = pivot?.suspicious?.[h] || 0
                  const bo = pivot?.bot?.[h] || 0
                  const be = pivot?.benign?.[h] || 0
                  const tot = sc + su + bo + be
                  return (
                    <tr key={h}>
                      <td className="mono" style={{ fontWeight: 600 }}>
                        {String(h).padStart(2, '0')}:00
                      </td>
                      <td className="mono">{sc.toLocaleString()}</td>
                      <td className="mono">{su.toLocaleString()}</td>
                      <td className="mono">{bo.toLocaleString()}</td>
                      <td className="mono">{be.toLocaleString()}</td>
                      <td className="mono" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                        {tot.toLocaleString()}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Filtered Activity */}
      {activeTab === 'filtered_activity' && (
        <div className="chart-container">
          <div className="chart-title">Targeted Subset Filtering: Bot & Internal Activity</div>
          <p style={{ fontSize: '.8rem', color: 'var(--text-muted)', marginBottom: 16 }}>
            Practical 07 filters isolates specific threat actor cohorts: internal enterprise subnets (10.0.0.0/8, 192.168.0.0/16)
            and high-entropy bot sessions to analyze lateral movement and unauthorized crawling.
          </p>

          <div
            style={{
              background: '#0a0a0a',
              padding: 16,
              borderRadius: 6,
              border: '1px solid var(--border)',
              fontFamily: 'var(--font-mono)',
              fontSize: '.75rem',
              color: '#a1a1aa',
              lineHeight: 1.6,
            }}
          >
            <div style={{ color: 'var(--accent)' }}># Pandas Filtering Logic Executed:</div>
            <div>internal_mask = df['ip'].str.startswith(('10.', '192.168.'))</div>
            <div>bot_mask = df['label'] == 'bot'</div>
            <div>filtered_df = df[internal_mask | bot_mask]</div>
            <div>filtered_df.to_csv('Data/processed/filtered_activity.csv', index=False)</div>
          </div>

          <div style={{ marginTop: 20 }}>
            <h4 style={{ fontSize: '.9rem', fontWeight: 600, marginBottom: 8 }}>Key Insights from Filtered Slice:</h4>
            <ul style={{ fontSize: '.8rem', color: 'var(--text-secondary)', paddingLeft: 20, lineHeight: 1.8 }}>
              <li>Internal network hosts exhibited 0 scanner events, validating firewall boundary isolation.</li>
              <li>Bot activity is distributed evenly across 24 hours without nocturnal lull, characteristic of cron-driven scrapers.</li>
              <li>Directory fuzzer tool user-agents are exclusively confined to public external IP spaces.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
